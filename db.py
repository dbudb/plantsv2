"""Database setup/config: how the app connects to Postgres."""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Copies the values from .env into os.environ (locally). On Render the env vars are
# set by the server and there is no .env; then this does nothing.
load_dotenv()

# Render's DB URL has no driver part ("postgresql://..."), so SQLAlchemy would look
# for psycopg2, which isn't installed. We always use pg8000.
# os.environ[...] (not .get): without DB_URL the app stops at once with a KeyError.
DB_URL = os.environ["DB_URL"].replace("postgresql://", "postgresql+pg8000://", 1)

# The engine holds the connections to the DB (a pool) and is created once.
db_engine = create_engine(DB_URL)

# A factory for sessions. A route calls SessionLocal() to get one session (one
# conversation with the DB) per request.
SessionLocal = sessionmaker(db_engine)
