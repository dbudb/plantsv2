# Plant Tracker

Backend MVP for a plant tracker. Built with FastAPI, SQLAlchemy, Alembic and PostgreSQL.

- **Species** are a shared catalogue of what a plant needs (watering interval, light as
  DLI). `POST /species/lookup` finds a species by name; if the database doesn't know it,
  Gemini fills in the data.
- **Plants** belong to a user and link to a species.
- **Care events** (watering, fertilizing, repotting, ...) document a plant's history.
- **Login** with JWT. Everything except signup and login needs a token.

**Live:** https://plantsv2-8t8y.onrender.com/docs (Swagger UI). The free server sleeps after 15 minutes without
traffic, so the first request can take about a minute.

**Database schema:** [diagram on dbdiagram.io](https://dbdiagram.io/embed#c=Ly8gUGxhbnQgVHJhY2tlciBkYXRhYmFzZSwgd3JpdHRlbiBmcm9tIG1vZGVscy5weS4KLy8gRGlhZ3JhbTogcGFzdGUgaW50byBkYmRpYWdyYW0uaW8sIG9yIHNlZSB0aGUgbGluayBpbiBSRUFETUUubWQuCgpUYWJsZSB1c2VycyB7CiAgaWQgaW50ZWdlciBbcGssIGluY3JlbWVudF0KICBlbWFpbCB2YXJjaGFyIFtub3QgbnVsbCwgdW5pcXVlLCBub3RlOiAnc2F2ZWQgbG93ZXJjYXNlJ10KICBuYW1lIHZhcmNoYXIgW25vdCBudWxsXQogIHBhc3N3b3JkX2hhc2ggdmFyY2hhciBbbm90IG51bGxdCn0KClRhYmxlIHNwZWNpZXMgewogIGlkIGludGVnZXIgW3BrLCBpbmNyZW1lbnRdCiAgbmFtZSB2YXJjaGFyIFtub3QgbnVsbCwgbm90ZTogJ2NvbW1vbiBuYW1lLCBlLmcuIFRvbWF0ZSddCiAgYm90YW5pY2FsX25hbWUgdmFyY2hhciBbdW5pcXVlLCBub3RlOiAnZS5nLiBTb2xhbnVtIGx5Y29wZXJzaWN1bSddCiAgd2F0ZXJpbmdfaW50ZXJ2YWwgaW50ZWdlciBbbm90IG51bGwsIG5vdGU6ICdkYXlzJ10KICBtaW5fZGxpIGZsb2F0IFtub3QgbnVsbCwgbm90ZTogJ21vbC9twrIvZGF5J10KICBtYXhfZGxpIGZsb2F0IFtub3QgbnVsbCwgbm90ZTogJ21vbC9twrIvZGF5J10KfQoKVGFibGUgcGxhbnRzIHsKICBpZCBpbnRlZ2VyIFtwaywgaW5jcmVtZW50XQogIHVzZXJfaWQgaW50ZWdlciBbbm90IG51bGwsIHJlZjogPiB1c2Vycy5pZF0KICBzcGVjaWVzX2lkIGludGVnZXIgW25vdCBudWxsLCByZWY6ID4gc3BlY2llcy5pZF0KICBuYW1lIHZhcmNoYXIgW25vdCBudWxsXQogIGxvY2F0aW9uIHZhcmNoYXIgW25vdCBudWxsXQogIGNyZWF0ZWRfYXQgdGltZXN0YW1wIFtub3QgbnVsbCwgZGVmYXVsdDogYG5vdygpYF0KfQoKVGFibGUgY2FyZV9ldmVudHMgewogIGlkIGludGVnZXIgW3BrLCBpbmNyZW1lbnRdCiAgcGxhbnRfaWQgaW50ZWdlciBbbm90IG51bGwsIHJlZjogPiBwbGFudHMuaWRdCiAgZXZlbnRfdHlwZSBldmVudF90eXBlIFtub3QgbnVsbCwgbm90ZTogJ3N0b3JlZCBhcyB2YXJjaGFyKDUwKSddCiAgYW1vdW50IGZsb2F0IFtub3RlOiAndW5pdCBkZXBlbmRzIG9uIHRoZSB0eXBlOiBtbCB3YXRlci9mZXJ0aWxpemVyLCBsaXRlcnMgc29pbCwgZ3JhbXMnXQogIHRpbWVzdGFtcCB0aW1lc3RhbXAgW25vdCBudWxsXQogIG5vdGVzIHZhcmNoYXIKfQoKRW51bSBldmVudF90eXBlIHsKICBXQVRFUklORwogIEZFUlRJTElaSU5HCiAgUkVQT1RUSU5HCiAgSEFSVkVTVElORwogIFNPV0lORwogIEFDUVVJUkVECiAgVFJJTU1JTkcKfQo%3D) (source: `schema.dbml`).

## Endpoints

| Method | Path | What it does |
|---|---|---|
| POST | `/signup` | create a user (JSON: email, name, password) |
| POST | `/login` | get a token (form: username = email, password) |
| GET | `/me` | the logged-in user |
| PATCH | `/me` | change name, email or password |
| DELETE | `/me` | delete the user, with their plants and care events |
| GET | `/species` | all species |
| POST | `/species` | add a species by hand |
| POST | `/species/lookup` | find a species by name; ask Gemini if it's unknown |
| GET | `/species/{id}` | one species |
| PATCH | `/species/{id}` | change a species |
| DELETE | `/species/{id}` | delete a species (409 while plants use it) |
| GET | `/plants` | your plants |
| POST | `/plants` | add a plant |
| GET | `/plants/{id}` | one of your plants |
| PATCH | `/plants/{id}` | change a plant |
| DELETE | `/plants/{id}` | delete a plant, with its care events |
| GET | `/plants/{id}/events` | a plant's care events, oldest first |
| POST | `/plants/{id}/events` | add a care event |
| GET | `/events/{id}` | one care event |
| PATCH | `/events/{id}` | change a care event |
| DELETE | `/events/{id}` | delete a care event |

All routes except `/`, `/signup` and `/login` need the token: log in with the
**Authorize** button in `/docs`.

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

## Deployment

Runs on [Render](https://render.com), set up by the Blueprint in `render.yaml`: a free
Postgres database and a free web service, both in Frankfurt. Every push to `master` builds
and deploys again.

- Build: `pip install -r requirements.txt`
- Start: `alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port $PORT`
  (the migrations run on every start)
- Env vars: `DB_URL` comes from the database, `SECRET_KEY` is generated by Render,
  `GEMINI_API_KEY` is entered once in the Render dashboard.
