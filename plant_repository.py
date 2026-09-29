"""Handles the databases reads and writes into and from the plants table"""

from models import CareEvent, Plant
from sqlalchemy import delete, select


def create_plant(session, species_id, name, location):
    plant = Plant(species_id=species_id, name=name, location=location)
    session.add(plant)
    session.commit()
    session.refresh(plant)
    return plant

def read_plant(session):
    return session.scalars(select(Plant)).all()

def delete_plant(session, plant_id: int):
    plant = session.get(Plant, plant_id)
    if plant is None:
        return None
    session.execute(delete(CareEvent).where(CareEvent.plant_id == plant_id))
    session.delete(plant)
    session.commit()
    return plant

def update_plant(session, plant_id: int, species_id, name, location):
    plant = session.get(Plant, plant_id)
    if plant is None:
        return None
    if species_id is not None:
        plant.species_id = species_id
    if name is not None:
        plant.name = name
    if location is not None:
        plant.location = location
    session.commit()
    session.refresh(plant)
    return plant
