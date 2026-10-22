# To-do (MVP check against Notion, 2026-10-15)

## Missing for the MVP
- [x] **Validation:** add value rules to the inputs (negative/empty values,
      `min_dli` bigger than `max_dli`, ...). Check what `POST /plants` does with a
      `species_id` that doesn't exist; compare with `PATCH /plants`.
- [x] **Migrations:** one clean initial migration, remove `alembic/versions` from
      `.gitignore`, commit it (see DECISIONS.md). Without it, `alembic upgrade head`
      fails after a clone and on the server.
- [x] **Push:** master is in sync with GitHub.
- [x] **User endpoints:** PATCH `/me` (name, email, password) and DELETE `/me`
      (also deletes the user's plants and their care events). Week 5 asks for CRUD
      on all relevant tables.
- [x] **Deploy** on Render with env vars (`DB_URL`, `SECRET_KEY`, `GEMINI_API_KEY`)
      and a build pipeline: https://plantsv2-8t8y.onrender.com/docs
- [x] **DB schema:** diagram on dbdiagram.io (DBML), link in README.
- [x] **README:** endpoint list and live URL.
- [x] **Slides:** presentation for week 6 (claude.ai artifact, private until shared).
- [ ] **Notion page:** title and description are in. Still open: links for
      "Datenbank Schema", "Bereitgestellte App-URL", "Präsentationsfolie"; dates unknown.
- [ ] **Free Render DB expires 2026-11-21** (deleted 2026-12-05): recreate or upgrade
      before the presentation if it's later.

## Already done
- REST API with FastAPI
- PostgreSQL with users, species, plants, care_events (full CRUD)
- JWT auth (signup, login, `/me` with GET/PATCH/DELETE, all routes protected)
- No UI
