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
   SECRET_KEY=any-long-random-string
   GEMINI_API_KEY=your-gemini-api-key
   ```
   `SECRET_KEY` signs the login tokens. Generate one with
   `python -c "import secrets; print(secrets.token_hex(32))"`.
   `GEMINI_API_KEY` is for the species lookup (`POST /species/lookup`); create one in
   Google AI Studio. The app doesn't start without both keys.

3. Create the tables:
   ```
   python -m alembic upgrade head
   ```

## Run

```
python -m uvicorn main:app --reload
```

Then open http://127.0.0.1:8000/docs to try the endpoints in Swagger UI.
