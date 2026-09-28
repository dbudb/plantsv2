"""Defines what the API sends in it's HTTP response body."""

from datetime import datetime
from pydantic import BaseModel, ConfigDict

from models import EventType

class SpeciesOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    watering_interval: int
    max_dli: float
    min_dli: float


class PlantOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    species_id: int
    name: str
    location: str
    created_at: datetime


class CareEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    plant_id: int
    event_type: EventType
    amount: float | None
    timestamp: datetime
    notes: str | None
