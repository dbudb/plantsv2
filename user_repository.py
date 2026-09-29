"""Handles the databases reads and writes into and from the users table"""

from models import User
from sqlalchemy import select


def create_user(session, email, name, password_hash):
    user = User(email=email, name=name, password_hash=password_hash)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def read_user_by_email(session, email: str):
    return session.scalars(select(User).where(User.email == email)).first()
