"""Handles the databases reads and writes into and from the species table"""

from models import Species
from sqlalchemy import select

def create_species(session, name, watering_interval, min_dli, max_dli):
    species = Species(
        name=name, watering_interval=watering_interval, min_dli=min_dli, max_dli=max_dli
    )
    session.add(species)
    session.commit()
    session.refresh(species)
    return species

def read_species(session):
    return session.scalars(select(Species)).all()

def delete_species(session, species_id: int):
    species = session.get(Species, species_id)
    if species is None:
        return None
    session.delete(species)
    session.commit()
    return species