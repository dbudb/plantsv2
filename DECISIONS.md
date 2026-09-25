# Decisions

## Setup
- Postgres in Docker (container `plants-db`). SQLite not allowed.
- pip + `requirements.txt`, no uv. Update with
  `python -m pip freeze | Out-File -Encoding utf8 requirements.txt`
  (plain `>` in PowerShell writes UTF-16, which git treats as binary).
- DB password in code for now, move to `.env` later.

## Before the first push (to-do)
- [ ] Move the DB URL into `.env`, add `.env` to `.gitignore`, `db.py` reads it from there.
- [ ] Give the DB a new password (the old one is in the git history).
- [ ] One clean initial migration, un-ignore `alembic/versions/`, commit it.

- **Migrations while developing:** `alembic/versions/` is in `.gitignore` for now.
  Before the first push: generate ONE clean initial migration, remove the line
  from `.gitignore`, commit it. After pushing, never edit a migration, only add new ones.

## Structure (repository pattern)
- `db.py` — connection (engine, SessionLocal)
- `models.py` — tables (how data is **stored**)
- `schemas.py` — Pydantic models (what the API **sends back**, later also receives)
- `species_repository.py` — all DB functions for species
- `plant_repository.py` — all DB functions for plants (not built yet)
- `main.py` — routes

## How a request flows
`/docs` → route in `main.py` → repository function → Postgres → back to the route
→ schema turns it into the JSON reply.

- **Repository functions take the session as a parameter.** The route opens it,
  the repository only uses it.
- **Routes open the session with `with SessionLocal() as session:`.** It closes
  automatically, even on a crash. Without closing, every request leaks a DB connection.
- **`session.refresh(obj)` after `commit()`.** Commit wipes the loaded values; refresh
  reloads them (incl. the new `id`) while the session is still open. Without it:
  `DetachedInstanceError` when FastAPI reads the object after the session is gone.
- **Schemas separate from models**, even though they look the same for species now.
  They will differ later (e.g. password hash never sent back; input has no `id`).
  SQLModel (one class for both) was considered, not used.
- **Schemas need `model_config = ConfigDict(from_attributes=True)`** so Pydantic can
  read DB objects (`obj.name`), not only dicts.
- **Don't use a DB model as return type** (`-> Species`): FastAPI crashes on startup.
  Use the schema (`-> SpeciesOut`).
- Route inputs are query parameters for now.

## Data model
- Tables: `users`, `species`, `plants`, `care_events`
- **Species** holds the needs: watering interval, sunlight, temperature.
  Why: all tomatoes need the same, so store it once.
- Sunlight is stored as **DLI** (Daily Light Integral, float). The backend derives
  shade / partial sun / full sun from it; the user can see both, or enter a measured DLI.
  Species stores a range: `min_dli` and `max_dli`.
- **Plant** holds name, actual location, and links to species and user.
- Multiple plants of the same species are allowed, so name ≠ species.
- No "indoor" flag on species. Any plant can live indoors if the conditions fit.
  Whether a place suits a plant is calculated from its needs vs. the conditions.
- **Plant dates:** only `created_at` (added to app, automatic).
  No `born_at`: the real start is an origin event (see below).
- **Event types:** Python Enum in code (not a table), because the code needs to
  react to them (e.g. watering → reminder). New type = one new line.
- **Origin events:** SOWING or ACQUIRED mark the real start of a plant. They can be
  dated in the past (event has its own timestamp). `created_at` is only technical.
- Later: ask the user "do you know when you sowed/got this?" and add the origin event.
- **Care events** link to the plant (`plant_id`), not the other way round.
  All events of a plant sorted by time = its documentation.
- Care event has one `amount` column (nullable). The event type decides what it means:
  watering = ml water, fertilizing = ml fertilizer, repotting = liters soil,
  harvest = grams (maybe). Pruning etc. have no amount.
  Unit isn't stored; the backend derives it from the type.
  Open: `notes` field for extras like which fertilizer?
- Build step by step: `species` first, then `plants`, then the rest.
  Species first because `plants.species_id` needs an existing species.
- Species data is entered by hand for now (via `/docs`), filled in batches later.
  Gemini just produces data and calls the same `create_species` later.

## Features
- Gemini identifies the species and fills in its needs.
- Later: warn when a plant's location doesn't fit its species' needs.
