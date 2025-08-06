from sqlalchemy import Column, Integer, String, create_engine, Boolean, BigInteger, func, select
from sqlalchemy.orm import DeclarativeBase, Session, joinedload, selectinload, sessionmaker, relationship, backref
from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session
import datetime
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse



engine = create_engine(
    "mysql+pymysql://gen_user:hamsterdev1@89.169.45.136:3306/default_db", #   
    connect_args={"ssl": {"ssl_disabled": False}},
)


class Base(DeclarativeBase):
    created_at = Column(Integer, default=datetime.datetime.now(datetime.timezone.utc).timestamp())


class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    tg_id = Column(BigInteger)
    username = Column(String(255))
    full_name = Column(String(255))
    phone = Column(String(255))
    city = Column(String(255))
    balance = Column(Integer, default=0)
    inner_balance = Column(Integer, default=0)
    has_ended = Column(Boolean, default=False)
    ref = Column(BigInteger)
    ref_level = Column(Integer, default=1)

class City(Base):
    __tablename__ = 'cities'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    text = Column(String(255))
    agent_account = Column(String(255))
    channel_link = Column(String(255))

class Schedule(Base):
    __tablename__ = 'schedules'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    city = Column(Integer)
    start = Column(String(255))

class PayMetadata(Base):
    __tablename__ = 'pay_metadatas'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    price = Column(Integer)
    product = Column(String(255))
    procent_balance = Column(Integer)
    inner_balance = Column(Integer)
    has_payed = Column(Boolean, default=False)
    
class BalanceTransfer(Base):
    __tablename__ = "balance_transafers"
    
    id = Column(Integer, primary_key=True)
    to_user_id = Column(Integer)
    from_user_id = Column(Integer)
    money = Column(Integer)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Зависимость FastAPI для получения сессии
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()

app.add_middleware(
  CORSMiddleware,
  allow_origins = ["*"],
  allow_methods = ["*"],
  allow_headers = ["*"]
)

@app.get("/admin/users")
def get_users_admin():
    with Session(engine) as session:
        users = session.execute(select(User)).scalars().all()

        user_ids = [user.id for user in users]
        user_tg_ids = [user.tg_id for user in users]

        # Словари для быстрого доступа
        user_by_tg_id = {user.tg_id: user for user in users}
        user_by_id = {user.id: user for user in users}

        # Получаем все оплаты всех пользователей одной пачкой
        pay_rows = session.execute(
            select(
                PayMetadata.user_id,
                PayMetadata.created_at,
                PayMetadata.price,
                PayMetadata.product,
                PayMetadata.has_payed
            ).where(PayMetadata.user_id.in_(user_ids))
        ).all()

        # Строим индексы по user_id
        pays_by_user = {}
        for row in pay_rows:
            pays_by_user.setdefault(row.user_id, []).append(row)

        # Словарь: tg_id -> список прямых рефералов
        refs_map = {}
        for user in users:
            if user.ref:
                refs_map.setdefault(user.ref, []).append(user)

        def get_structure_and_sum(start_user, depth=20):
            visited = set()
            total_sum = 0
            queue = [(start_user.tg_id, 0)]
            while queue:
                ref_tg_id, level = queue.pop(0)
                if level >= depth:
                    continue
                for ref_user in refs_map.get(ref_tg_id, []):
                    if ref_user.id in visited:
                        continue
                    visited.add(ref_user.id)
                    for p in pays_by_user.get(ref_user.id, []):
                        if p.has_payed:
                            total_sum += p.price
                    queue.append((ref_user.tg_id, level + 1))
            return len(visited), total_sum

        end_users = []

        for user in users:
            user_pays = pays_by_user.get(user.id, [])
            paid_pays = [p for p in user_pays if p.has_payed]

            try:
                last_pay = max([p.created_at for p in paid_pays]) if paid_pays else 0
            except:
                last_pay = 0

            total_pays = sum([p.price for p in paid_pays])

            first_line_refs = refs_map.get(user.tg_id, [])
            total_refs, structure_sum = get_structure_and_sum(user)

            # Метки
            tags = []
            if any(p.product == "clubtraining" for p in paid_pays):
                tags.append("орг клуба")
            if any(p.product == "game" for p in paid_pays):
                tags.append("вед игры")
            if any(p.product == "package" for p in paid_pays):
                tags.append("сетевик")
            if len(tags) == 0:
                tags.append("участник")

            # Пригласитель
            ref_user = user_by_tg_id.get(user.ref)
            ref_username = ref_user.username if ref_user else None
            
            total_purchases = {
                "subscribe-1": "Подписка на месяц",
                "subscribe-12": "Подписка на год",
                "poster": "Афиша",
                "package": "Пакет",
                "game": "Ведущий игры",
                "clubtraining": "Орг. клуба",
            }
            
            purchases = [
                    f"{total_purchases.get(p.product)} {p.price}₽ {datetime.datetime.utcfromtimestamp(p.created_at).strftime('%d.%m.%Y')}"
                    for p in paid_pays
                ]
            if len(purchases) == 0:
                purchases.append("Ничего")
            end_users.append({
                "name": user.full_name,
                "username": user.username,
                "tg_id": user.tg_id,
                "phone": user.phone,
                "city": user.city,
                "reg_date": datetime.datetime.utcfromtimestamp(user.created_at).strftime('%Y-%m-%d %H:%M:%S'),
                "balance": user.balance,
                "inner_balance": user.inner_balance,
                "last_pay": datetime.datetime.utcfromtimestamp(last_pay).strftime('%Y-%m-%d %H:%M:%S') if last_pay != 0 else "Никогда",
                "1_line_refs": len(first_line_refs),
                "line_refs": total_refs,
                'total_pays': total_pays,
                "ref": ref_username,
                "ref_level": user.ref_level,
                "total_structure_buys": structure_sum + total_pays,
                "user_tag": ", ".join(tags),
                "purchases": purchases
            })

        return end_users
    

@app.get("/admin/pays")
def get_pays_admin():
    with Session(engine) as session:
        end_pays = []
        pays = session.execute(select(PayMetadata).where(PayMetadata.has_payed == True)).scalars().all()
        for pay in pays:
            end_pays.append({
                "id": pay.id,
                "buyed": {"game": "Ведущий игры", "package": "Пакет", "clubtraining": "Организатор клуба", "subscribe-1": "Подписка на месяц", "subscribe-12": "Подписка на год", }.get(pay.product, pay.product),
                "from": session.execute(select(User).where(User.id == pay.user_id)).scalar().username,
                "price": pay.price,
                "date": datetime.datetime.utcfromtimestamp(pay.created_at).strftime('%Y-%m-%d %H:%M:%S'),
                "status": "Оплачено"
            })
    return end_pays

@app.get("/admin/transfers")
def get_transfers_admin():
    with Session(engine) as session:
        end_transfers = []
        transfers = session.execute(select(BalanceTransfer)).scalars().all()
        for transfer in transfers:
            end_transfers.append({
                "id": transfer.id,
                "from": session.execute(select(User).where(User.id == transfer.from_user_id)).scalar().username,
                "to": session.execute(select(User).where(User.id == transfer.to_user_id)).scalar().username,
                "money": transfer.money,
                "date": datetime.datetime.utcfromtimestamp(transfer.created_at).strftime('%Y-%m-%d %H:%M:%S'),
            })
    return end_transfers


@app.get("/")
def get_index():
    file_inner = open("./build/index.html", 'r').read()
    return HTMLResponse(content=file_inner)

@app.get("/assets/{file}")
def get_asset_file(file):
    return FileResponse(path=f"./build/assets/{file}")