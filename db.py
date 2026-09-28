"""Database setup/config"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

DB_URL = os.environ["DB_URL"]

db_engine = create_engine(DB_URL)

SessionLocal = sessionmaker(db_engine)
