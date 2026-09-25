from fastapi import FastAPI, HTTPException

from db import SessionLocal
from species_repository import create_species, read_species, delete_species
from schemas import SpeciesOut

print("file loading")
app = FastAPI()

plants = []


@app.get("/")
def hello():
    print("hello called")
    return {"message": "hello plants"}


print("hello registered")


@app.get("/plants")
def plants():
    return plants


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
