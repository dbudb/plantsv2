"""Handles the database reads and writes into and from the plants table.

Same pattern as species_repository.py: add/commit/refresh, None if not found.
"""

from models import CareEvent, Plant
from sqlalchemy import delete, select


def create_plant(session, user_id, species_id, name, location):
    plant = Plant(user_id=user_id, species_id=species_id, name=name, location=location)
    session.add(plant)
    session.commit()
    session.refresh(plant)
    return plant

# Only the plants of this user.
def read_plant(session, user_id: int):
    return session.scalars(select(Plant).where(Plant.user_id == user_id)).all()

# None if the plant doesn't exist or belongs to someone else. The routes use this as
# the ownership check before every change.
def read_one_plant(session, plant_id: int, user_id: int):
    plant = session.get(Plant, plant_id)
    if plant is None or plant.user_id != user_id:
        return None
    return plant

def delete_plant(session, plant_id: int):
    plant = session.get(Plant, plant_id)
    if plant is None:
        return None
    # Events first: they point to the plant (foreign key), so Postgres would refuse
    # to delete a plant that still has events.
    session.execute(delete(CareEvent).where(CareEvent.plant_id == plant_id))
    session.delete(plant)
    # One commit for both: either everything is deleted or nothing.
    session.commit()
    return plant

# PATCH: only fields that were sent (not None) are changed.
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
