"""Defines what the API receives and sends in its HTTP bodies."""

from datetime import datetime
from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    StringConstraints,
    model_validator,
)

from models import EventType

# Rules, written once and reused by the input classes below.
NonEmptyText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
AboveZero = Annotated[int, Field(gt=0)]
ZeroOrMore = Annotated[float, Field(ge=0, allow_inf_nan=False)]


class UserIn(BaseModel):
    email: EmailStr
    name: NonEmptyText
    password: str = Field(min_length=8)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    name: str


class SpeciesIn(BaseModel):
    name: NonEmptyText
    watering_interval: AboveZero
    min_dli: ZeroOrMore
    max_dli: ZeroOrMore

    @model_validator(mode="after")
    def check_dli_range(self):
        if self.min_dli > self.max_dli:
            raise ValueError("min_dli is bigger than max_dli")
        return self


class SpeciesUpdate(BaseModel):
    name: NonEmptyText | None = None
    watering_interval: AboveZero | None = None
    min_dli: ZeroOrMore | None = None
    max_dli: ZeroOrMore | None = None


class SpeciesOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    watering_interval: int
    max_dli: float
    min_dli: float


class PlantIn(BaseModel):
    species_id: int
    name: NonEmptyText
    location: NonEmptyText


class PlantUpdate(BaseModel):
    species_id: int | None = None
    name: NonEmptyText | None = None
    location: NonEmptyText | None = None


class PlantOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    species_id: int
    name: str
    location: str
    created_at: datetime


class CareEventIn(BaseModel):
    event_type: EventType
    timestamp: datetime
    amount: ZeroOrMore | None = None
    notes: str | None = None


class CareEventUpdate(BaseModel):
    event_type: EventType | None = None
    timestamp: datetime | None = None
    amount: ZeroOrMore | None = None
    notes: str | None = None


class CareEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    plant_id: int
    event_type: EventType
    amount: float | None
    timestamp: datetime
    notes: str | None
