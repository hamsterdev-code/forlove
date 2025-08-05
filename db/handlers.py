from sqlalchemy.orm import Session
from sqlalchemy import select
from db.connect import engine
from db.models import User

def get_user(session: Session, tg_id: int):
    user = session.execute(select(User).where(User.tg_id == tg_id)).scalar()
    return user

def create_user(session: Session, tg_id: int, full_name: str, username: str, ref: str = 1):
    user = User(
        tg_id = tg_id,
        username = username,
        full_name = full_name,
        phone = "",
        city = "",
        ref = ref
    )
    
    session.add(user)
    session.commit()
    
    return user