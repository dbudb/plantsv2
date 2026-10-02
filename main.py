from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from db import SessionLocal
from species_repository import (
    create_species,
    read_species,
    read_one_species,
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
from user_repository import create_user, read_user_by_email
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
    UserOut,
    SpeciesIn,
    SpeciesUpdate,
    SpeciesOut,
    PlantIn,
    PlantUpdate,
    PlantOut,
    CareEventIn,
    CareEventUpdate,
    CareEventOut,
)

print("file loading")
app = FastAPI()


@app.get("/")
def hello():
    print("hello called")
    return {"message": "hello plants"}


print("hello registered")


@app.post("/signup")
def signup(data: UserIn) -> UserOut:
    email = data.email.lower()
    with SessionLocal() as session:
        if read_user_by_email(session, email) is not None:
            raise HTTPException(status_code=409, detail="email already registered")
        user = create_user(session, email, data.name, hash_password(data.password))
    return user


@app.post("/login")
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()]):
    with SessionLocal() as session:
        user = read_user_by_email(session, form.username.lower())
    if user is None or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail="wrong email or password")
    return {"access_token": create_token(user.id), "token_type": "bearer"}


@app.get("/me")
def me(user: CurrentUser) -> UserOut:
    return user


@app.get("/plants")
def get_plants(user: CurrentUser) -> list[PlantOut]:
    with SessionLocal() as session:
        plants = read_plant(session, user.id)
    return plants


@app.post("/plants")
def add_plant(user: CurrentUser, data: PlantIn) -> PlantOut:
    with SessionLocal() as session:
        if session.get(Species, data.species_id) is None:
            raise HTTPException(status_code=404, detail="species not found")
        plant = create_plant(
            session, user.id, data.species_id, data.name, data.location
        )
    return plant


@app.get("/plants/{plant_id}")
def get_plant(user: CurrentUser, plant_id: int) -> PlantOut:
    with SessionLocal() as session:
        plant = read_one_plant(session, plant_id, user.id)
        if plant is None:
            raise HTTPException(status_code=404)
        return plant


@app.patch("/plants/{plant_id}")
def change_plant(user: CurrentUser, plant_id: int, data: PlantUpdate) -> PlantOut:
    with SessionLocal() as session:
        if read_one_plant(session, plant_id, user.id) is None:
            raise HTTPException(status_code=404)
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
        plant = delete_plant(session, plant_id)
        return plant


@app.get("/plants/{plant_id}/events")
def get_care_events(user: CurrentUser, plant_id: int) -> list[CareEventOut]:
    with SessionLocal() as session:
        if read_one_plant(session, plant_id, user.id) is None:
            raise HTTPException(status_code=404)
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


@app.get("/species", dependencies=[Depends(get_current_user)])
def get_species() -> list[SpeciesOut]:

    with SessionLocal() as session:
        species = read_species(session)
    return species


@app.post("/species", dependencies=[Depends(get_current_user)])
def add_species(data: SpeciesIn) -> SpeciesOut:
    with SessionLocal() as session:
        species = create_species(
            session, data.name, data.watering_interval, data.min_dli, data.max_dli
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
        new_min = species.min_dli if data.min_dli is None else data.min_dli
        new_max = species.max_dli if data.max_dli is None else data.max_dli
        if new_min > new_max:
            raise HTTPException(
                status_code=422, detail="min_dli is bigger than max_dli"
            )
        species = update_species(
            session,
            species_id,
            data.name,
            data.watering_interval,
            data.min_dli,
            data.max_dli,
        )
        return species


@app.delete("/species/{species_id}", dependencies=[Depends(get_current_user)])
def remove_species(species_id: int) -> SpeciesOut:
    with SessionLocal() as session:
        has_plants = session.scalars(
            select(Plant).where(Plant.species_id == species_id)
        ).first()
        if has_plants:
            raise HTTPException(status_code=409, detail="species still has plants")
        species = delete_species(session, species_id)
        if species is None:
            raise HTTPException(status_code=404)
        return species
