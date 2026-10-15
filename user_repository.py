"""Handles the databases reads and writes into and from the users table"""

from models import CareEvent, Plant, User
from sqlalchemy import delete, select


def create_user(session, email, name, password_hash):
    user = User(email=email, name=name, password_hash=password_hash)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def read_user_by_email(session, email: str):
    return session.scalars(select(User).where(User.email == email)).first()

def update_user(session, user_id: int, email, name, password_hash):
    user = session.get(User, user_id)
    if user is None:
        return None
    if email is not None:
        user.email = email
    if name is not None:
        user.name = name
    if password_hash is not None:
        user.password_hash = password_hash
    session.commit()
    session.refresh(user)
    return user

def delete_user(session, user_id: int):
    user = session.get(User, user_id)
    if user is None:
        return None
    # Events have no user_id: find them through the ids of the user's plants.
    plant_ids = select(Plant.id).where(Plant.user_id == user_id)
    session.execute(delete(CareEvent).where(CareEvent.plant_id.in_(plant_ids)))
    session.execute(delete(Plant).where(Plant.user_id == user_id))
    session.delete(user)
    session.commit()
    return user
