# To-do (MVP check against Notion, 2026-09-29)

## Missing for the MVP
- [ ] **Validation:** add value rules to the inputs (negative/empty values,
      `min_dli` bigger than `max_dli`, ...). Check what `POST /plants` does with a
      `species_id` that doesn't exist; compare with `PATCH /plants`.
- [ ] **Migrations:** one clean initial migration, remove `alembic/versions` from
      `.gitignore`, commit it (see DECISIONS.md). Without it, `alembic upgrade head`
      fails after a clone and on the server.
- [x] **Push:** master is in sync with GitHub. Push again after the migrations.
- [ ] **Deploy** on Render/Vercel with env vars (`DB_URL`, `SECRET_KEY`) and a build pipeline.
- [ ] **README:** add the endpoint list and the live URL after deploying.
- [ ] **Notion page:** fill in "Datenbank Schema", "Bereitgestellte App-URL",
      "Präsentationsfolie" and the dates.

## Already done
- REST API with FastAPI
- PostgreSQL with users, species, plants, care_events (full CRUD)
- JWT auth (signup, login, `/me`, all routes protected)
- No UI
