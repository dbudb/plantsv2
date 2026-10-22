"""Handles the database reads and writes into and from the species table.

Repository = the only place that talks to the DB. Every function gets the session
from the route, so one request uses one session (and the route decides when it closes).
"""

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
    # add: remember the object; commit: really write it to the DB.
    session.add(species)
    session.commit()
    # commit wipes the loaded values; refresh reloads them, incl. the new id from
    # Postgres. Without it: DetachedInstanceError when FastAPI reads the object later.
    session.refresh(species)
    return species

def read_species(session):
    # scalars: the Species objects themselves, not rows of tuples.
    return session.scalars(select(Species)).all()

# session.get looks up by primary key; None if there is no such id.
def read_one_species(session, species_id: int):
    return session.get(Species, species_id)

# Matches the common OR the botanical name, ignoring case on both sides
# ("tomate" finds "Tomate").
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

# Only the botanical name, for the "already exists" (409) check.
def read_species_by_botanical_name(session, botanical_name: str):
    return session.scalars(
        select(Species).where(
            func.lower(Species.botanical_name) == botanical_name.lower()
        )
    ).first()

def delete_species(session, species_id: int):
    species = session.get(Species, species_id)
    if species is None:
        return None
    session.delete(species)
    session.commit()
    # The deleted object still holds its values; the route sends them back.
    return species

# PATCH: only fields that were sent (not None) are changed.
def update_species(
    session, species_id: int, name, botanical_name, watering_interval, min_dli, max_dli
):
    species = session.get(Species, species_id)
    if species is None:
        return None
    if name is not None:
        species.name = name
    if botanical_name is not None:
        species.botanical_name = botanical_name
    if watering_interval is not None:
        species.watering_interval = watering_interval
    if min_dli is not None:
        species.min_dli = min_dli
    if max_dli is not None:
        species.max_dli = max_dli
    # Changing attributes is enough: the session notices it and commit writes an UPDATE.
    session.commit()
    session.refresh(species)
    return species
