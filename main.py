from fastapi import FastAPI
from sqlalchemy import Column, Integer, String, create_engine, Boolean, BigInteger, select
from sqlalchemy.orm import DeclarativeBase, Session
import datetime

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


def get_user_refs(session: Session, user: User):
    users = session.execute(select(User).where(User.ref == user.tg_id)).scalars().all()
    line_users = []
    for i in range(0, 20):
        line_users.append(len(users))
        users = get_list_refs(session, users)
    return line_users
def get_list_refs(session: Session, users: list):
    l = []
    for user in users:
        l.extend(session.execute(select(User).where(User.ref == user.tg_id, User.ref != 1)).scalars().all())
    return l


app = FastAPI()
@app.get("/admin/users")
def get_users_admin():
    with Session(engine) as session:
        end_users = []
        users = session.execute(select(User)).scalars().all()
        for user in users:
            try: last_pay = max(session.execute(select(PayMetadata.created_at).where(PayMetadata.has_payed == True, PayMetadata.user_id == user.id)).scalars().all())
            except: last_pay = 0
            
            total_pays = sum(session.execute(select(PayMetadata.price).where(PayMetadata.has_payed == True, PayMetadata.user_id == user.id)).scalars().all())
            
            
            users = session.execute(select(User).where(User.ref == user.tg_id)).scalars().all()
            user_refs = []
            total_structure_buys = 0
            total_structure_buys += total_pays
            for i in range(0, 20):
                user_refs.append(len(users))
                for u in users:
                    total_structure_buys += sum(session.execute(select(PayMetadata.price).where(PayMetadata.has_payed == True, PayMetadata.user_id == u.id)).scalars().all())
                users = get_list_refs(session, users)
            user_tag = ""
            #if 
            end_users.append({
                "name": user.full_name,
                "tg_id": user.tg_id,
                "phone": user.phone,
                "city": user.city,
                "reg_date": datetime.datetime.utcfromtimestamp(user.created_at).strftime('%Y-%m-%d %H:%M:%S'),
                "balance": user.balance,
                "inner_balance": user.inner_balance,
                "last_pay": datetime.datetime.utcfromtimestamp(last_pay).strftime('%Y-%m-%d %H:%M:%S') if last_pay != 0 else "Никогда",
                "1_line_refs": user_refs[0],
                "line_refs": sum(user_refs),
                'total_pays': total_pays,
                "ref": (session.execute(select(User).where(User.tg_id == user.ref)).scalar()).username,
                "ref_level": user.ref_level,
                "total_structure_buys": total_structure_buys
            })
        return end_users