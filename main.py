from datetime import datetime

from typing import Annotated

from fastapi import Depends, FastAPI, Form, HTTPException
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
from auth import create_token, hash_password, verify_password
from models import EventType, Plant, Species
from schemas import UserOut, SpeciesOut, PlantOut, CareEventOut

print("file loading")
app = FastAPI()

@app.get("/")
def hello():
    print("hello called")
    return {"message": "hello plants"}


print("hello registered")


@app.post("/signup")
def signup(
    email: Annotated[str, Form()],
    name: Annotated[str, Form()],
    password: Annotated[str, Form()],
) -> UserOut:
    with SessionLocal() as session:
        if read_user_by_email(session, email) is not None:
            raise HTTPException(status_code=409, detail="email already registered")
        user = create_user(session, email, name, hash_password(password))
    return user


@app.post("/login")
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()]):
    with SessionLocal() as session:
        user = read_user_by_email(session, form.username)
    if user is None or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail="wrong email or password")
    return {"access_token": create_token(user.id), "token_type": "bearer"}


@app.get("/plants")
def get_plants() -> list[PlantOut]:
    with SessionLocal() as session:
        plants = read_plant(session)
    return plants


@app.post("/plants")
def add_plant(species_id: int, name: str, location: str) -> PlantOut:
    with SessionLocal() as session:
        plant = create_plant(session, species_id, name, location)
    return plant


@app.get("/plants/{plant_id}")
def get_plant(plant_id: int) -> PlantOut:
    with SessionLocal() as session:
        plant = read_one_plant(session, plant_id)
        if plant is None:
            raise HTTPException(status_code=404)
        return plant


@app.patch("/plants/{plant_id}")
def change_plant(
    plant_id: int,
    species_id: int | None = None,
    name: str | None = None,
    location: str | None = None,
) -> PlantOut:
    with SessionLocal() as session:
        if species_id is not None and session.get(Species, species_id) is None:
            raise HTTPException(status_code=404, detail="species not found")
        plant = update_plant(session, plant_id, species_id, name, location)
        if plant is None:
            raise HTTPException(status_code=404)
        return plant


@app.delete("/plants/{plant_id}")
def remove_plant(plant_id: int) -> PlantOut:
    with SessionLocal() as session:
        plant = delete_plant(session, plant_id)
        if plant is None:
            raise HTTPException(status_code=404)
        return plant


@app.get("/plants/{plant_id}/events")
def get_care_events(plant_id: int) -> list[CareEventOut]:
    with SessionLocal() as session:
        care_events = read_care_events(session, plant_id)
    return care_events


@app.post("/plants/{plant_id}/events")
def add_care_event(
    plant_id: int,
    event_type: EventType,
    timestamp: datetime,
    amount: float | None = None,
    notes: str | None = None,
) -> CareEventOut:
    with SessionLocal() as session:
        if session.get(Plant, plant_id) is None:
            raise HTTPException(status_code=404)
        care_event = create_care_event(
            session, plant_id, event_type, amount, timestamp, notes
        )
    return care_event


@app.get("/events/{event_id}")
def get_care_event(event_id: int) -> CareEventOut:
    with SessionLocal() as session:
        care_event = read_one_care_event(session, event_id)
        if care_event is None:
            raise HTTPException(status_code=404)
        return care_event


@app.patch("/events/{event_id}")
def change_care_event(
    event_id: int,
    event_type: EventType | None = None,
    timestamp: datetime | None = None,
    amount: float | None = None,
    notes: str | None = None,
) -> CareEventOut:
    with SessionLocal() as session:
        care_event = update_care_event(
            session, event_id, event_type, amount, timestamp, notes
        )
        if care_event is None:
            raise HTTPException(status_code=404)
        return care_event


@app.delete("/events/{event_id}")
def remove_care_event(event_id: int) -> CareEventOut:
    with SessionLocal() as session:
        care_event = delete_care_event(session, event_id)
        if care_event is None:
            raise HTTPException(status_code=404)
        return care_event


@app.get("/species")
def get_species() -> list[SpeciesOut]:

    with SessionLocal() as session:
        species = read_species(session)
    return species


@app.post("/species")
def add_species(
    name: str, watering_interval: int, min_dli: float, max_dli: float
) -> SpeciesOut:
    with SessionLocal() as session:
        species = create_species(session, name, watering_interval, min_dli, max_dli)
    return species


@app.get("/species/{species_id}")
def get_one_species(species_id: int) -> SpeciesOut:
    with SessionLocal() as session:
        species = read_one_species(session, species_id)
        if species is None:
            raise HTTPException(status_code=404)
        return species


@app.patch("/species/{species_id}")
def change_species(
    species_id: int,
    name: str | None = None,
    watering_interval: int | None = None,
    min_dli: float | None = None,
    max_dli: float | None = None,
) -> SpeciesOut:
    with SessionLocal() as session:
        species = update_species(
            session, species_id, name, watering_interval, min_dli, max_dli
        )
        if species is None:
            raise HTTPException(status_code=404)
        return species


@app.delete("/species/{species_id}")
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
