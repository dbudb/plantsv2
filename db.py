"""Database setup/config"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

# Render's DB URL has no driver part ("postgresql://..."), so SQLAlchemy would look
# for psycopg2, which isn't installed. We always use pg8000.
DB_URL = os.environ["DB_URL"].replace("postgresql://", "postgresql+pg8000://", 1)

db_engine = create_engine(DB_URL)

SessionLocal = sessionmaker(db_engine)
