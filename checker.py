

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session, DeclarativeBase
from sqlalchemy import Column, Integer, String, create_engine, Boolean, BigInteger, select
import uvicorn
from yoomoney import Client
from threading import Thread
import time
import datetime
from telebot import TeleBot, types
from yookassa import Configuration, Payment


SECRET_API = "live_8sy3urnb4lO3FxsGsaxANT4wC20ZMT97Fb-PAnCD7Sk"
SHOP_ID = 1124758
engine = create_engine(
    "mysql+pymysql://gen_user:hamsterdev1@89.169.45.136:3306/default_db", #   sqlite:///server.db
    connect_args={"ssl": {"required": True}}  # или {"ssl": True}
)
bot = TeleBot("7713812500:AAFBkZRpgYKbatoUkj0N-niA-5nXbYWZOJg")
Configuration.configure(SHOP_ID, SECRET_API)

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

def ref_handler(session: Session, user: User, pay_metadata: PayMetadata):
    user_ref = get_user_ref(session, user)
    admin_user = session.execute(select(User).where(User.id == 1)).scalar()
    total_pay_moneys = pay_metadata.price * (pay_metadata.procent_balance / 100)
    total_inner_pay_moneys = pay_metadata.price * (pay_metadata.inner_balance / 100)
    for i in range(1, 13):
        need_level = need_ref_level(i)
        pay_moneys = total_pay_moneys * get_ref_procent(i) / 100
        inner_pay_moneys = total_inner_pay_moneys * get_ref_inner_procent(i) / 100
        print(pay_moneys)
        if user_ref.ref_level >= need_level: 
            user_ref.balance += pay_moneys # начисление денег
            user_ref.inner_balance += inner_pay_moneys # начисление денег
        else:
            admin_user.inner_balance += inner_pay_moneys # начисление денег
            admin_user.balance += pay_moneys
        print(i, user_ref.id)  
        user_ref = get_user_ref(session, user_ref)              
    session.commit()
def get_user_ref(session: Session, user: User):
    if user.ref == 1:
        return session.execute(select(User).where(User.id == user.ref)).scalar()
    return session.execute(select(User).where(User.tg_id == user.ref)).scalar()
def need_ref_level(line: int):
    if line == 1: return 1
    if line == 2 or line == 3: return 2
    if line == 4 or line == 5: return 3
    if line == 6 or line == 7: return 4
    if line == 8 or line == 9: return 5
    if line > 9: return 6
def get_ref_procent(line: int):
    if line == 1: return 40
    if line == 2: return 20
    if line == 3: return 14
    if line == 4: return 6
    if line == 5: return 6
    if line == 6: return 4
    if line == 7: return 4
    if line == 8: return 3
    if line == 9: return 2
    if line == 10: return 0.5
    if line == 11: return 0.25
    if line == 12: return 0.125 
def get_ref_inner_procent(line: int):
    if line == 1: return 40
    if line == 2: return 40
    if line == 3: return 20
    else: return 0

ADMIN_ACCOUNT = 6062822304

app = FastAPI()

def checker():
    while True:
        with Session(engine) as session:
            payments = Payment.list({"limit": 100})
            for payment in payments.items:
                print(payment.id, payment.paid, payment.amount.value)
                if not payment.metadata["orderNumber"] or payment.paid == False: continue
                pay_metadata_id = int(payment.metadata["orderNumber"])
                pay_metadata = session.execute(select(PayMetadata).where(PayMetadata.id == pay_metadata_id)).scalar()
                if pay_metadata == None or pay_metadata.has_payed == True: continue
                user = session.execute(select(User).where(User.id == pay_metadata.user_id)).scalar()
                
                pay_metadata.has_payed = True
                
                if pay_metadata.product == "package":
                    if pay_metadata.price == 5000: user.ref_level = 2
                    if pay_metadata.price == 15000: user.ref_level = 3
                    if pay_metadata.price == 25000: user.ref_level = 4
                    if pay_metadata.price == 45000: user.ref_level = 5
                    if pay_metadata.price == 100000: user.ref_level = 6
                
                bot.send_message(ADMIN_ACCOUNT, f"""
    Пользователь @{user.username} купил {"подписку" if pay_metadata.product.startswith("subscribe") else "продукт"} на {pay_metadata} рублей
                                    """)
                if pay_metadata.product.startswith("subscribe"):
                    bot.send_message(user.tg_id, "Для получения дальнейших инструкций обратитесь к @Forlove2025")
                elif pay_metadata.product != "package":
                    bot.send_message(user.tg_id, "Для получения дальнейших инструкций обратитесь к @Forlove2025")
                else:
                    bot.send_message(user.tg_id, "Увеличен заработок с реферальной программы")
                
                ref_handler(session, user, pay_metadata)
                
                session.commit()
        time.sleep(10)
        
@app.get("/pay")
def check_pay():
    payments = Payment.list({"limit": 100})
    with Session(engine) as session:
        for payment in payments.items:
            print(payment.id, payment.paid, payment.amount.value)
            if not payment.metadata["orderNumber"] or payment.paid == False: continue
            pay_metadata_id = int(payment.metadata["orderNumber"])
            pay_metadata = session.execute(select(PayMetadata).where(PayMetadata.id == pay_metadata_id)).scalar()
            if pay_metadata == None or pay_metadata.has_payed == True: continue
            user = session.execute(select(User).where(User.id == pay_metadata.user_id)).scalar()
            
            pay_metadata.has_payed = True
            
            if pay_metadata.product == "package":
                if pay_metadata.price == 5000: user.ref_level = 2
                if pay_metadata.price == 15000: user.ref_level = 3
                if pay_metadata.price == 25000: user.ref_level = 4
                if pay_metadata.price == 45000: user.ref_level = 5
                if pay_metadata.price == 100000: user.ref_level = 6
            
            bot.send_message(ADMIN_ACCOUNT, f"""
Пользователь @{user.username} купил {"подписку" if pay_metadata.product.startswith("subscribe") else "продукт"} на {pay_metadata} рублей
                                """)
            if pay_metadata.product.startswith("subscribe"):
                bot.send_message(user.tg_id, "Для получения дальнейших инструкций обратитесь к @Forlove2025")
            elif pay_metadata.product != "package":
                bot.send_message(user.tg_id, "Для получения дальнейших инструкций обратитесь к @Forlove2025")
            else:
                bot.send_message(user.tg_id, "Увеличен заработок с реферальной программы")
            
            ref_handler(session, user, pay_metadata)
            
            session.commit()
    return HTMLResponse("""
<h2>Перенаправление на бота</h2>
<script>window.open("https://t.me/forlove2025_bot", '_blank')</script>
""")

checker_thread = Thread(target=checker)
checker_thread.start()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)