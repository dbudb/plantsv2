"""Password hashing and JWT login"""

import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash

from db import SessionLocal
from models import User

SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = "HS256"
TOKEN_MINUTES = 30

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)


def create_token(user_id: int) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_MINUTES)
    return jwt.encode({"sub": str(user_id), "exp": expires}, SECRET_KEY, ALGORITHM)


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    try:
        user_id = int(jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])["sub"])
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="invalid token")
    with SessionLocal() as session:
        user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="invalid token")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
