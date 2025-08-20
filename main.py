from typing import List, Dict, Any
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, text, select, Column, Integer, String, BigInteger, Boolean
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
import datetime
DATABASE_URL = "mysql+pymysql://gen_user:hamsterdev1@89.169.45.136:3306/default_db"

# Подключение к MySQL
engine = create_engine(DATABASE_URL, connect_args={"ssl": {"ssl_disabled": False}}, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI(title="User Tree API")

# Разрешения CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ограничить в продакшене
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Модель ответа
class NodeOut(BaseModel):
    username: str
    tg_id: int
    children: List["NodeOut"] = []

    class Config:
        orm_mode = True

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

NodeOut.update_forward_refs()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def build_user_data(session: Session, user: User, users, pays_by_user, refs_map, user_by_tg_id):
    user_pays = pays_by_user.get(user.id, [])
    paid_pays = [p for p in user_pays if p.has_payed]
    for p in paid_pays: print(p.id)
    try:
        last_pay = max([p.created_at for p in paid_pays]) if paid_pays else 0
    except:
        last_pay = 0

    total_pays = sum([p.price for p in paid_pays])

    first_line_refs = refs_map.get(user.tg_id, [])

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

    total_refs, structure_sum = get_structure_and_sum(user)

    tags = []
    if any(p.product == "clubtraining" for p in paid_pays):
        tags.append("орг клуба")
    if any(p.product == "game" for p in paid_pays):
        tags.append("вед игры")
    if any(p.product == "package" for p in paid_pays):
        tags.append("сетевик")

    ref_user = user_by_tg_id.get(user.ref)
    ref_username = ref_user.username if ref_user else None
    
    purchases = [
            f"{p.product} {p.price} {datetime.datetime.utcfromtimestamp(p.created_at).strftime('%Y-%m-%d')}"
            for p in paid_pays
    ]
    if len(purchases) == 0:
        purchases = ["Ничего"]

    return {
        "name": user.full_name,
        "tg_id": user.tg_id,
        "phone": user.phone,
        "city": user.city,
        "reg_date": datetime.datetime.utcfromtimestamp(user.created_at).strftime('%Y-%m-%d %H:%M:%S'),
        "balance": user.balance,
        "inner_balance": user.inner_balance,
        "last_pay": datetime.datetime.utcfromtimestamp(last_pay).strftime('%Y-%m-%d %H:%M:%S') if last_pay != 0 else "Никогда",
        "1_line_refs": len(first_line_refs),
        "line_refs": total_refs,
        "total_pays": total_pays,
        "ref": ref_username,
        "ref_level": user.ref_level,
        "total_structure_buys": structure_sum + total_pays,
        "user_tag": " ".join(tags),
        "purchases": purchases
    }



@app.get("/users/{tg_id}/structure", response_model=NodeOut)
def get_user_structure(tg_id: int, db=Depends(get_db)):
    """
    Возвращает дерево пользователей начиная с пользователя с tg_id.
    Максимальная глубина — 20 уровней.
    """
    # Рекурсивный запрос в MySQL 8+
    sql = text("""
        WITH RECURSIVE tree AS (
            SELECT id, tg_id, username, ref, 1 AS depth
            FROM users
            WHERE tg_id = :tg_id
          UNION ALL
            SELECT u.id, u.tg_id, u.username, u.ref, t.depth + 1
            FROM users u
            JOIN tree t ON u.ref = t.tg_id
            WHERE t.depth < 20
        )
        SELECT tg_id, username, ref
        FROM tree;
    """)

    rows = db.execute(sql, {"tg_id": tg_id}).fetchall()

    if not rows:
        raise HTTPException(status_code=404, detail="User not found or has no subtree")

    # Создаём структуру дерева за один проход
    nodes: Dict[int, Dict[str, Any]] = {}
    children_map: Dict[int, List[int]] = {}

    for tg, username, ref in rows:
        nodes[tg] = {
            "username": username or f"tg_{tg}",
            "tg_id": tg,
            "children": []
        }
        if ref is not None:
            children_map.setdefault(ref, []).append(tg)

    # Связываем детей с родителями
    for parent_tg, kids in children_map.items():
        if parent_tg in nodes:
            nodes[parent_tg]["children"].extend(nodes[kid] for kid in kids if kid in nodes)

    # Корень — это tg_id из запроса
    root_node = nodes.get(tg_id)
    if not root_node:
        raise HTTPException(status_code=404, detail="Root user not found")

    return root_node


@app.get("/users/{username}/data")
def get_single_user(username: str):
    with Session(engine) as session:
        users = session.execute(select(User)).scalars().all()
        user_ids = [u.id for u in users]
        user_by_tg_id = {u.tg_id: u for u in users}

        target_user = session.execute(select(User).where(User.username == username)).scalar()
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")

        pay_rows = session.execute(
            select(PayMetadata).where(PayMetadata.user_id.in_(user_ids))
        ).scalars().all()

        pays_by_user = {}
        for p in pay_rows:
            pays_by_user.setdefault(p.user_id, []).append(p)

        refs_map = {}
        for u in users:
            if u.ref:
                refs_map.setdefault(u.ref, []).append(u)

        return build_user_data(session, target_user, users, pays_by_user, refs_map, user_by_tg_id)
    
@app.get("/")
def get_index():
    file_inner = open("./build/index.html", 'r').read()
    return HTMLResponse(content=file_inner)

@app.get("/assets/{file}")
def get_asset_file(file):
    return FileResponse(path=f"./build/assets/{file}")