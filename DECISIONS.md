# Decisions

## Setup
- Postgres in Docker (container `plants-db`). SQLite not allowed.
- pip + `requirements.txt`, no uv. Update with
  `python -m pip freeze | Out-File -Encoding utf8 requirements.txt`
  (plain `>` in PowerShell writes UTF-16, which git treats as binary).
- DB password in code for now, move to `.env` later.

## Structure (repository pattern)
- `db.py` — connection (engine, SessionLocal)
- `models.py` — tables
- `plant_repository.py` — all DB functions for plants
- `main.py` — routes

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

## Features
- Gemini identifies the species and fills in its needs.
- Later: warn when a plant's location doesn't fit its species' needs.
