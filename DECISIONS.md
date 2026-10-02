# Decisions

## Setup
- Postgres in Docker (container `plants-db`). SQLite not allowed.
- pip + `requirements.txt`, no uv. Update with
  `python -m pip freeze | Out-File -Encoding utf8 requirements.txt`
  (plain `>` in PowerShell writes UTF-16, which git treats as binary).
- DB password in code for now, move to `.env` later.

## Before the first push (to-do)
- [x] Move the DB URL into `.env`, add `.env` to `.gitignore`, `db.py` reads it from there.
- [x] Give the DB a new password (the old one is in the git history).
- [x] One clean initial migration, un-ignore `alembic/versions/`, commit it.

- **Migrations:** `alembic/versions/` is in git, starting with one clean initial
  migration. After pushing, never edit a migration, only add new ones.

## Structure (repository pattern)
- `db.py` — connection (engine, SessionLocal)
- `models.py` — tables (how data is **stored**)
- `schemas.py` — Pydantic models (what the API **receives** and **sends back**)
- `species_repository.py` — all DB functions for species
- `plant_repository.py` — all DB functions for plants (not built yet)
- `main.py` — routes

## How a request flows
`/docs` → input class in `schemas.py` checks the JSON body → route in `main.py`
→ repository function → Postgres → back to the route → schema turns it into the JSON reply.

- **Repository functions take the session as a parameter.** The route opens it,
  the repository only uses it.
- **Routes open the session with `with SessionLocal() as session:`.** It closes
  automatically, even on a crash. Without closing, every request leaks a DB connection.
- **`session.refresh(obj)` after `commit()`.** Commit wipes the loaded values; refresh
  reloads them (incl. the new `id`) while the session is still open. Without it:
  `DetachedInstanceError` when FastAPI reads the object after the session is gone.
- **Schemas separate from models**, even though they look the same for species now.
  They will differ later (e.g. password hash never sent back; input has no `id`).
- **Schemas need `model_config = ConfigDict(from_attributes=True)`** so Pydantic can
  read DB objects (`obj.name`), not only dicts.
- **Don't use a DB model as return type** (`-> Species`): FastAPI crashes on startup.
  Use the schema (`-> SpeciesOut`).
- Route inputs are JSON bodies, checked by input classes in `schemas.py`
  (`...In` for create, `...Update` for PATCH). Login stays a form: the Authorize
  button in `/docs` needs it.

## Validation
- An input class checks the body **before** the route runs. A broken rule answers 422
  and nothing is saved.
- **Each rule is written once** as a named type at the top of `schemas.py` and reused:
  `NonEmptyText` (trimmed, at least 1 character), `AboveZero`, `ZeroOrMore` (no `inf`/`nan`).
- Rules:
  - species name, plant name, plant location, user name: not empty; only spaces counts
    as empty; spaces around the value are cut off
  - `watering_interval`: bigger than 0
  - `min_dli`, `max_dli`, care event `amount`: 0 or bigger
  - `min_dli` not bigger than `max_dli`. On create the class checks it. On PATCH the
    route checks it against the stored values, because a class can't look into the DB.
  - plant `species_id`: the species must exist (404 "species not found")
  - signup: valid email (`EmailStr`, package `email-validator`), password at least 8 characters
- **Emails are lowercase everywhere:** signup saves lowercase, login lowercases what was typed.
- PATCH: a field that is missing or `null` stays unchanged.
- Unknown fields in a body are ignored (Pydantic default).

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
