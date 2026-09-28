from fastapi import FastAPI, HTTPException

from db import SessionLocal
from species_repository import create_species, read_species, delete_species
from plant_repository import create_plant, read_plant, delete_plant
from schemas import SpeciesOut, PlantOut

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
        species = delete_species(session, species_id)
        if species is None:
            raise HTTPException(status_code=404)
        return species
