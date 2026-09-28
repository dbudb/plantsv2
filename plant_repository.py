"""Handles the databases reads and writes into and from the plants table"""

from models import Plant
from sqlalchemy import select


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
    session.delete(plant)
    session.commit()
    return plant
