# Plant Tracker

Backend MVP for a plant tracker: create, read, update and delete plants.
Built with FastAPI, SQLAlchemy, Alembic and PostgreSQL.

## Setup

1. Clone the repo and create a virtual environment:
   ```
   git clone git@github.com:dbudb/plantsv2.git
   cd plantsv2
   python -m venv .venv
   .venv\Scripts\activate
   python -m pip install -r requirements.txt
   ```

2. Create a PostgreSQL database and a `.env` file in the project root:
   ```
   DB_URL=postgresql+pg8000://USER:PASSWORD@localhost:5432/DB_NAME
   ```

3. Create the tables:
   ```
   python -m alembic upgrade head
   ```

## Run

```
python -m uvicorn main:app --reload
```

Then open http://127.0.0.1:8000/docs to try the endpoints in Swagger UI.
