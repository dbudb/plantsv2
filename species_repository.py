"""Handles the databases reads and writes into and from the species table"""

from models import Species
from sqlalchemy import func, or_, select

def create_species(session, name, botanical_name, watering_interval, min_dli, max_dli):
    species = Species(
        name=name,
        botanical_name=botanical_name,
        watering_interval=watering_interval,
        min_dli=min_dli,
        max_dli=max_dli,
    )
    session.add(species)
    session.commit()
    session.refresh(species)
    return species

def read_species(session):
    return session.scalars(select(Species)).all()

def read_one_species(session, species_id: int):
    return session.get(Species, species_id)

def read_species_by_name(session, name: str):
    name = name.lower()
    return session.scalars(
        select(Species).where(
            or_(
                func.lower(Species.name) == name,
                func.lower(Species.botanical_name) == name,
            )
        )
    ).first()

def delete_species(session, species_id: int):
    species = session.get(Species, species_id)
    if species is None:
        return None
    session.delete(species)
    session.commit()
    return species

def update_species(session, species_id: int, name, watering_interval, min_dli, max_dli):
    species = session.get(Species, species_id)
    if species is None:
        return None
    if name is not None:
        species.name = name
    if watering_interval is not None:
        species.watering_interval = watering_interval
    if min_dli is not None:
        species.min_dli = min_dli
    if max_dli is not None:
        species.max_dli = max_dli
    session.commit()
    session.refresh(species)
    return species
