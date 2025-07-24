from fastapi import FastAPI
from sqladmin import Admin, ModelView
from sqlalchemy.orm import Session, DeclarativeBase
from sqlalchemy import Column, Integer, String, create_engine, Boolean, BigInteger, select
import datetime
import uvicorn


engine = create_engine(
    "mysql+pymysql://gen_user:hamsterdev1@89.169.45.136:3306/default_db", #   sqlite:///server.db
    connect_args={"ssl": {"required": True}}  # или {"ssl": True}
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


app = FastAPI()
admin = Admin(app, engine)


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.username, User.full_name, User.ref, User.balance, User.inner_balance, User.ref_level, User.city]
class CityAdmin(ModelView, model=City):
    column_list = [City.id, City.name]
class ScheduleAdmin(ModelView, model=Schedule):
    column_list = [Schedule.id, Schedule.name, Schedule.city, Schedule.start]
class PayMetadataAdmin(ModelView, model=PayMetadata):
    column_list = [PayMetadata.id, PayMetadata.user_id, PayMetadata.price, PayMetadata.product, PayMetadata.has_payed]


admin.add_view(UserAdmin)
admin.add_view(CityAdmin)
admin.add_view(ScheduleAdmin)
admin.add_view(PayMetadataAdmin)