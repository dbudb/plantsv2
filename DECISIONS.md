# Decisions

## Setup
- Postgres in Docker (container `plants-db`). SQLite not allowed.
- pip + `requirements.txt`, no uv. Update with `python -m pip freeze > requirements.txt`.
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
- **Plant** holds name, actual location, and links to species and user.
- Multiple plants of the same species are allowed, so name ≠ species.
- No "indoor" flag on species. Any plant can live indoors if the conditions fit.
  Whether a place suits a plant is calculated from its needs vs. the conditions.
- Build step by step: `species` first, then `plants`, then the rest.

## Features
- Gemini identifies the species and fills in its needs.
- Later: warn when a plant's location doesn't fit its species' needs.
