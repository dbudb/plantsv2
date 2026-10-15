# To-do (MVP check against Notion, 2026-10-15)

## Missing for the MVP
- [x] **Validation:** add value rules to the inputs (negative/empty values,
      `min_dli` bigger than `max_dli`, ...). Check what `POST /plants` does with a
      `species_id` that doesn't exist; compare with `PATCH /plants`.
- [x] **Migrations:** one clean initial migration, remove `alembic/versions` from
      `.gitignore`, commit it (see DECISIONS.md). Without it, `alembic upgrade head`
      fails after a clone and on the server.
- [x] **Push:** master is in sync with GitHub.
- [ ] **User endpoints:** PATCH `/me` (name, email, password) and DELETE `/me`
      (also deletes the user's plants and their care events). Week 5 asks for CRUD
      on all relevant tables.
- [ ] **Deploy** on Render/Vercel with env vars (`DB_URL`, `SECRET_KEY`, `GEMINI_API_KEY`)
      and a build pipeline. The app doesn't start if one is missing.
- [ ] **DB schema:** diagram on dbdiagram.io (DBML), link in README and Notion.
- [ ] **README:** add the endpoint list and the live URL after deploying.
- [ ] **Slides:** presentation for week 6, link in Notion.
- [ ] **Notion page:** fill in "Datenbank Schema", "Bereitgestellte App-URL",
      "Präsentationsfolie" and the dates.

## Already done
- REST API with FastAPI
- PostgreSQL with users, species, plants, care_events (full CRUD for species, plants
  and care events; users only have signup, login and `/me` so far)
- JWT auth (signup, login, `/me`, all routes protected)
- No UI
