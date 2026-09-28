"""Database setup/config"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

PASSWORD = "QFbqDDpXRmPTCFtx8f9kh8jl" # ENV here later!

DB_URL = f"postgresql+pg8000://plants:{PASSWORD}@localhost:5432/plants" # can also live in env or seperate config

db_engine = create_engine(DB_URL)

SessionLocal = sessionmaker(db_engine)