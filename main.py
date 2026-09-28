from datetime import datetime

from fastapi import FastAPI, HTTPException
from sqlalchemy import select

from db import SessionLocal
from species_repository import create_species, read_species, delete_species
from plant_repository import create_plant, read_plant, delete_plant
from care_event_repository import (
    create_care_event,
    read_care_events,
    delete_care_event,
)
from models import EventType, Plant
from schemas import SpeciesOut, PlantOut, CareEventOut

print("file loading")
app = FastAPI()

@app.get("/")
def hello():
    print("hello called")
    return {"message": "hello plants"}


print("hello registered")


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
