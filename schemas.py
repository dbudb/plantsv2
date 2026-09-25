"""Defines what the API sends in it's HTTP response body."""

from pydantic import BaseModel, ConfigDict

class SpeciesOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    watering_interval: int
    max_dli: float
    min_dli: float

