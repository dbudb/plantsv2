# Decisions

## Setup
- Postgres in Docker (container `plants-db`). SQLite not allowed.
- pip + `requirements.txt`, no uv. Update with
  `python -m pip freeze | Out-File -Encoding utf8 requirements.txt`
  (plain `>` in PowerShell writes UTF-16, which git treats as binary).
- Secrets live in `.env` (git ignores it): `DB_URL` with the DB password, `SECRET_KEY`,
  `GEMINI_API_KEY`.

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
- `plant_repository.py` — all DB functions for plants
- `care_event_repository.py` — all DB functions for care events
- `user_repository.py` — all DB functions for users
- `auth.py` — password hashing, JWT tokens, `CurrentUser` (the logged-in user of a request)
- `gemini.py` — asks Gemini for species data
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
  - PATCH `/me`: the same rules as signup. A new email that another user already has
    answers 409; a new password is hashed like on signup.
- **Emails are lowercase everywhere:** signup and PATCH `/me` save lowercase, login
  lowercases what was typed.
- PATCH: a field that is missing or `null` stays unchanged.
- Unknown fields in a body are ignored (Pydantic default).

## Data model
- Tables: `users`, `species`, `plants`, `care_events`
- **Species** holds the needs: watering interval, sunlight, temperature.
  Why: all tomatoes need the same, so store it once.
- **Species has two names:** `name` (common, e.g. "Tomate") and `botanical_name`
  (e.g. "Solanum lycopersicum"). `botanical_name` is nullable, because old and
  hand-made rows have none, and unique: one row per botanical name.
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
- **Deleting:** a plant takes its care events with it. A user (DELETE `/me`) takes their
  plants and those plants' events with them. A species that still has plants can't be
  deleted (409), because those plants point to it.
- Build step by step: `species` first, then `plants`, then the rest.
  Species first because `plants.species_id` needs an existing species.
- Species data is entered by hand for now (via `/docs`), filled in batches later.
  Gemini just produces data and calls the same `create_species` later.
- **Schema diagram:** `schema.dbml` is written by hand from `models.py`. The dbdiagram.io
  link in the README and on Notion carries a copy of that file inside the link, so it
  needs no account. After a model change: update `schema.dbml`, then rebuild the link
  and replace it in the README and on Notion:
  `python -c "import base64,urllib.parse as u;print('https://dbdiagram.io/embed#c='+u.quote(base64.b64encode(open('schema.dbml','rb').read()).decode(),safe=''))"`

## Gemini species lookup
- `POST /species/lookup` takes a typed name (`{"name": "Tomate"}`) and answers a
  species. `POST /species` by hand stays. Photo input comes later as a second route.
- **Gemini is only asked when the DB doesn't know the name.** Flow: search the DB →
  miss: ask Gemini → search again with Gemini's botanical name → miss: `create_species`.
- **The search ignores case** and checks `name` and `botanical_name`. The names keep
  their capitals in the DB (unlike emails), because they are shown to users.
- **Second search:** "tomato" and "Tomate" lead to the same botanical name. Then the
  existing row is returned and nothing is saved.
- `name` of a new species is Gemini's common name in the typed language, not the
  typed text, so typos don't land in the DB.
- Gemini answers as structured JSON (package `google-genai`, code in `gemini.py`,
  key in `.env` as `GEMINI_API_KEY`). It is told the units: watering interval in
  days, DLI in mol/m²/day.
- **`generate_content`, not the newer `interactions` call:** in google-genai 2.28
  `interactions` raises error classes that only exist in a private module, so the
  public `errors.APIError` doesn't catch them.
- **20 s timeout, 3 attempts** on the client. Without a timeout a call hung for
  minutes; under load the model often answers 503, a retry usually works.
- Free tier: 5 requests per minute per model (429 above that). The DB search first
  keeps Gemini calls rare.
- The app doesn't start without `GEMINI_API_KEY`: the client is created when
  `gemini.py` loads.
- Gemini's data goes through `SpeciesIn`, so the same rules apply as for hand-made species.
- Errors: not a plant → 404 "species not found". Gemini unreachable, out of quota or
  its answer breaks the rules → 502. Nothing is saved in both cases.
- **A botanical name that already exists answers 409** on `POST /species` and
  `PATCH /species`. The check ignores case and only looks at `botanical_name`, not
  `name`. On PATCH a species doesn't collide with itself.
- Open: old rows without a botanical name can get a twin.

## Deployment (Render)
- **Blueprint `render.yaml`** creates everything: a free Postgres and a free web service,
  both in Frankfurt. Live: https://plantsv2-8t8y.onrender.com/docs
- Every push to `master` builds and deploys again (the build pipeline).
- **Migrations run in the start command** (`alembic upgrade head && uvicorn ...`): the
  free plan has no pre-deploy step and no shell.
- Env vars: `DB_URL` comes from the database, `SECRET_KEY` is generated by Render,
  `GEMINI_API_KEY` was entered once when the Blueprint was created (`sync: false`).
- `PYTHON_VERSION` 3.12.10 like local; Render's default is 3.14.
- Render's DB URL starts with `postgresql://`, so `db.py` swaps in the pg8000 driver.
- Free limits: the service sleeps after 15 minutes (first request then takes ~1 minute).
  **The free DB expires 30 days after creation (2026-11-21), deleted after 14 more days
  (2026-12-05).**
- A web service made by hand (not from the Blueprint) has no DB and no `DB_URL`: the app
  stops at start with `KeyError: 'DB_URL'`. Always create it from the Blueprint.

## Features
- Gemini identifies the species and fills in its needs.
- Later: warn when a plant's location doesn't fit its species' needs.
