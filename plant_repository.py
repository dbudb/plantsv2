"""Handles the databases reads and writes into and from the plants table"""

from models import CareEvent, Plant
from sqlalchemy import delete, select


def create_plant(session, user_id, species_id, name, location):
    plant = Plant(user_id=user_id, species_id=species_id, name=name, location=location)
    session.add(plant)
    session.commit()
    session.refresh(plant)
    return plant

def read_plant(session, user_id: int):
    return session.scalars(select(Plant).where(Plant.user_id == user_id)).all()

def read_one_plant(session, plant_id: int, user_id: int):
    plant = session.get(Plant, plant_id)
    if plant is None or plant.user_id != user_id:
        return None
    return plant

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
