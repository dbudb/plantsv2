"""All routes of the API.

Every route follows the same steps:
1. FastAPI checks the input. A JSON body goes through an input class from
   schemas.py (`...In`, `...Update`): broken values get a 422 before the route runs.
   `user: CurrentUser` runs auth.get_current_user first: no valid token, no route (401).
2. The route opens a DB session (`with SessionLocal() as session:`). The `with` closes
   it at the end, even on an error. Without it every request would leak a DB connection.
3. The route checks what the DB can't check by itself (does the plant belong to this
   user? does the species exist?) and answers 404/409 if not.
4. A repository function reads or writes the DB.
5. The return type (`-> PlantOut`) turns the DB object into the JSON reply. Only the
   fields listed in the schema are sent, so e.g. the password hash never leaves the server.
"""

from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from db import SessionLocal
from species_repository import (
    create_species,
    read_species,
    read_one_species,
    read_species_by_name,
    read_species_by_botanical_name,
    update_species,
    delete_species,
)
from plant_repository import (
    create_plant,
    read_plant,
    read_one_plant,
    update_plant,
    delete_plant,
)
from care_event_repository import (
    create_care_event,
    read_care_events,
    read_one_care_event,
    update_care_event,
    delete_care_event,
)
from user_repository import (
    create_user,
    read_user_by_email,
    update_user,
    delete_user,
)
from gemini import ask_gemini
from auth import (
    CurrentUser,
    create_token,
    get_current_user,
    hash_password,
    verify_password,
)
from models import Plant, Species
from schemas import (
    UserIn,
    UserUpdate,
    UserOut,
    SpeciesIn,
    SpeciesUpdate,
    SpeciesLookup,
    SpeciesOut,
    PlantIn,
    PlantUpdate,
    PlantOut,
    CareEventIn,
    CareEventUpdate,
    CareEventOut,
)

# The app. uvicorn starts it with `uvicorn main:app`; /docs is built from the routes below.
app = FastAPI()


# Open without a token: a quick "is the server up?" check.
@app.get("/")
def hello():
    return {"message": "hello plants"}


# ---------- Users ----------


@app.post("/signup")
def signup(data: UserIn) -> UserOut:
    # Emails are saved lowercase, so "Anna@x.de" and "anna@x.de" are the same user.
    email = data.email.lower()
    with SessionLocal() as session:
        # The column is unique: without this check Postgres would refuse it and the
        # user would get a 500 instead of a clear 409.
        if read_user_by_email(session, email) is not None:
            raise HTTPException(status_code=409, detail="email already registered")
        # Only the hash is stored, never the password itself.
        user = create_user(session, email, data.name, hash_password(data.password))
    return user


# A form, not JSON: the Authorize button in /docs sends a form (username + password).
# "username" is the email here.
@app.post("/login")
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()]):
    with SessionLocal() as session:
        user = read_user_by_email(session, form.username.lower())
    # Same answer for "unknown email" and "wrong password": nobody can find out
    # which emails are registered.
    if user is None or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail="wrong email or password")
    # The shape OAuth2 (and /docs) expects. The client sends this token with every
    # request after login.
    return {"access_token": create_token(user.id), "token_type": "bearer"}


# CurrentUser already loaded the user from the token, nothing left to do.
@app.get("/me")
def me(user: CurrentUser) -> UserOut:
    return user


@app.patch("/me")
def change_me(user: CurrentUser, data: UserUpdate) -> UserOut:
    # None means "don't change". A new email is lowercased and a new password hashed,
    # exactly like on signup.
    email = None if data.email is None else data.email.lower()
    password_hash = None if data.password is None else hash_password(data.password)
    with SessionLocal() as session:
        if email is not None:
            # Another user with this email ("twin") is a conflict; the own email is fine.
            twin = read_user_by_email(session, email)
            if twin is not None and twin.id != user.id:
                raise HTTPException(status_code=409, detail="email already registered")
        changed = update_user(session, user.id, email, data.name, password_hash)
        return changed


# Deletes the user with their plants and care events (see user_repository.delete_user).
@app.delete("/me")
def remove_me(user: CurrentUser) -> UserOut:
    with SessionLocal() as session:
        deleted = delete_user(session, user.id)
        return deleted


# ---------- Plants ----------
# A user only ever sees their own plants: every query filters by user.id.


@app.get("/plants")
def get_plants(user: CurrentUser) -> list[PlantOut]:
    with SessionLocal() as session:
        plants = read_plant(session, user.id)
    return plants


@app.post("/plants")
def add_plant(user: CurrentUser, data: PlantIn) -> PlantOut:
    with SessionLocal() as session:
        # Without this check the foreign key fails in Postgres: 500 instead of 404.
        if session.get(Species, data.species_id) is None:
            raise HTTPException(status_code=404, detail="species not found")
        # user_id comes from the token, not from the body: nobody can add plants to
        # someone else's account.
        plant = create_plant(
            session, user.id, data.species_id, data.name, data.location
        )
    return plant


@app.get("/plants/{plant_id}")
def get_plant(user: CurrentUser, plant_id: int) -> PlantOut:
    with SessionLocal() as session:
        # None if the plant doesn't exist OR belongs to someone else. Both answer 404,
        # so nobody learns which plant ids exist.
        plant = read_one_plant(session, plant_id, user.id)
        if plant is None:
            raise HTTPException(status_code=404)
        return plant


@app.patch("/plants/{plant_id}")
def change_plant(user: CurrentUser, plant_id: int, data: PlantUpdate) -> PlantOut:
    with SessionLocal() as session:
        # Ownership check first, then the change.
        if read_one_plant(session, plant_id, user.id) is None:
            raise HTTPException(status_code=404)
        # Only checked when the species is being changed.
        if (
            data.species_id is not None
            and session.get(Species, data.species_id) is None
        ):
            raise HTTPException(status_code=404, detail="species not found")
        plant = update_plant(
            session, plant_id, data.species_id, data.name, data.location
        )
        return plant


@app.delete("/plants/{plant_id}")
def remove_plant(user: CurrentUser, plant_id: int) -> PlantOut:
    with SessionLocal() as session:
        if read_one_plant(session, plant_id, user.id) is None:
            raise HTTPException(status_code=404)
        # Also deletes the plant's care events (see plant_repository.delete_plant).
        plant = delete_plant(session, plant_id)
        return plant


# ---------- Care events ----------
# Events belong to a plant. Access goes through the plant, so the same ownership
# check applies.


@app.get("/plants/{plant_id}/events")
def get_care_events(user: CurrentUser, plant_id: int) -> list[CareEventOut]:
    with SessionLocal() as session:
        if read_one_plant(session, plant_id, user.id) is None:
            raise HTTPException(status_code=404)
        # Sorted by timestamp: the plant's history, oldest first.
        care_events = read_care_events(session, plant_id)
    return care_events


@app.post("/plants/{plant_id}/events")
def add_care_event(user: CurrentUser, plant_id: int, data: CareEventIn) -> CareEventOut:
    with SessionLocal() as session:
        if read_one_plant(session, plant_id, user.id) is None:
            raise HTTPException(status_code=404)
        care_event = create_care_event(
            session, plant_id, data.event_type, data.amount, data.timestamp, data.notes
        )
    return care_event


# A single event is found by its own id. Events have no user_id, so
# read_one_care_event checks the owner through the event's plant.
@app.get("/events/{event_id}")
def get_care_event(user: CurrentUser, event_id: int) -> CareEventOut:
    with SessionLocal() as session:
        care_event = read_one_care_event(session, event_id, user.id)
        if care_event is None:
            raise HTTPException(status_code=404)
        return care_event


@app.patch("/events/{event_id}")
def change_care_event(
    user: CurrentUser, event_id: int, data: CareEventUpdate
) -> CareEventOut:
    with SessionLocal() as session:
        if read_one_care_event(session, event_id, user.id) is None:
            raise HTTPException(status_code=404)
        care_event = update_care_event(
            session, event_id, data.event_type, data.amount, data.timestamp, data.notes
        )
        return care_event


@app.delete("/events/{event_id}")
def remove_care_event(user: CurrentUser, event_id: int) -> CareEventOut:
    with SessionLocal() as session:
        if read_one_care_event(session, event_id, user.id) is None:
            raise HTTPException(status_code=404)
        care_event = delete_care_event(session, event_id)
        return care_event


# ---------- Species ----------
# Species are a shared catalogue for all users, so they have no owner.
# `dependencies=[Depends(get_current_user)]` still requires a token, but the route
# doesn't need to know who the user is.


@app.get("/species", dependencies=[Depends(get_current_user)])
def get_species() -> list[SpeciesOut]:

    with SessionLocal() as session:
        species = read_species(session)
    return species


@app.post("/species", dependencies=[Depends(get_current_user)])
def add_species(data: SpeciesIn) -> SpeciesOut:
    with SessionLocal() as session:
        # One row per real species. The check ignores case, so "solanum lycopersicum"
        # can't get in next to "Solanum lycopersicum".
        if (
            data.botanical_name is not None
            and read_species_by_botanical_name(session, data.botanical_name)
            is not None
        ):
            raise HTTPException(
                status_code=409, detail="botanical name already exists"
            )
        species = create_species(
            session,
            data.name,
            data.botanical_name,
            data.watering_interval,
            data.min_dli,
            data.max_dli,
        )
    return species


# Find a species by a typed name. Gemini is only asked when the DB doesn't know it:
# Gemini is slow and the free tier allows only 5 calls a minute.
@app.post("/species/lookup", dependencies=[Depends(get_current_user)])
def lookup_species(data: SpeciesLookup) -> SpeciesOut:
    with SessionLocal() as session:
        # 1. Search the DB by common or botanical name (case ignored).
        species = read_species_by_name(session, data.name)
        if species is not None:
            return species
        # 2. Unknown: ask Gemini. None means the text isn't a plant.
        #    (If Gemini fails, ask_gemini itself answers 502.)
        found = ask_gemini(data.name)
        if found is None:
            raise HTTPException(status_code=404, detail="species not found")
        # 3. Search again with Gemini's botanical name: "tomato" and "Tomate" are the
        #    same species, so the existing row is returned instead of a twin.
        species = read_species_by_name(session, found.botanical_name)
        if species is not None:
            return species
        # 4. Really new: save Gemini's data.
        species = create_species(
            session,
            found.name,
            found.botanical_name,
            found.watering_interval,
            found.min_dli,
            found.max_dli,
        )
    return species


@app.get("/species/{species_id}", dependencies=[Depends(get_current_user)])
def get_one_species(species_id: int) -> SpeciesOut:
    with SessionLocal() as session:
        species = read_one_species(session, species_id)
        if species is None:
            raise HTTPException(status_code=404)
        return species


@app.patch("/species/{species_id}", dependencies=[Depends(get_current_user)])
def change_species(species_id: int, data: SpeciesUpdate) -> SpeciesOut:
    with SessionLocal() as session:
        species = read_one_species(session, species_id)
        if species is None:
            raise HTTPException(status_code=404)
        # SpeciesUpdate can't check min <= max: maybe only one of them is sent, and a
        # schema can't see the stored value. So take the new value if sent, else the
        # stored one, and compare those.
        new_min = species.min_dli if data.min_dli is None else data.min_dli
        new_max = species.max_dli if data.max_dli is None else data.max_dli
        if new_min > new_max:
            raise HTTPException(
                status_code=422, detail="min_dli is bigger than max_dli"
            )
        if data.botanical_name is not None:
            # Same check as on create, but a species doesn't collide with itself.
            twin = read_species_by_botanical_name(session, data.botanical_name)
            if twin is not None and twin.id != species_id:
                raise HTTPException(
                    status_code=409, detail="botanical name already exists"
                )
        species = update_species(
            session,
            species_id,
            data.name,
            data.botanical_name,
            data.watering_interval,
            data.min_dli,
            data.max_dli,
        )
        return species


@app.delete("/species/{species_id}", dependencies=[Depends(get_current_user)])
def remove_species(species_id: int) -> SpeciesOut:
    with SessionLocal() as session:
        # Plants point to their species (foreign key). Deleting a species in use would
        # break them, so it's refused with 409. .first() is enough: one plant blocks it.
        has_plants = session.scalars(
            select(Plant).where(Plant.species_id == species_id)
        ).first()
        if has_plants:
            raise HTTPException(status_code=409, detail="species still has plants")
        species = delete_species(session, species_id)
        if species is None:
            raise HTTPException(status_code=404)
        return species
