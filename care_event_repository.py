"""Handles the databases reads and writes into and from the care_events table"""

from models import CareEvent, Plant
from sqlalchemy import select


def create_care_event(session, plant_id, event_type, amount, timestamp, notes):
    care_event = CareEvent(
        plant_id=plant_id,
        event_type=event_type,
        amount=amount,
        timestamp=timestamp,
        notes=notes,
    )
    session.add(care_event)
    session.commit()
    session.refresh(care_event)
    return care_event

def read_care_events(session, plant_id: int):
    return session.scalars(
        select(CareEvent)
        .where(CareEvent.plant_id == plant_id)
        .order_by(CareEvent.timestamp)
    ).all()

def read_one_care_event(session, event_id: int, user_id: int):
    care_event = session.get(CareEvent, event_id)
    if care_event is None or session.get(Plant, care_event.plant_id).user_id != user_id:
        return None
    return care_event

def delete_care_event(session, event_id: int):
    care_event = session.get(CareEvent, event_id)
    if care_event is None:
        return None
    session.delete(care_event)
    session.commit()
    return care_event

def update_care_event(session, event_id: int, event_type, amount, timestamp, notes):
    care_event = session.get(CareEvent, event_id)
    if care_event is None:
        return None
    if event_type is not None:
        care_event.event_type = event_type
    if amount is not None:
        care_event.amount = amount
    if timestamp is not None:
        care_event.timestamp = timestamp
    if notes is not None:
        care_event.notes = notes
    session.commit()
    session.refresh(care_event)
    return care_event
