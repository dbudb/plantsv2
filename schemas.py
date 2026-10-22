"""Defines what the API receives and sends in its HTTP bodies.

Three kinds of classes per table:
- `...In`: body of a create (POST). Required fields have no default.
- `...Update`: body of a PATCH. Every field defaults to None = "don't change".
- `...Out`: what is sent back. Only the listed fields leave the server.

Pydantic checks a body before the route runs. A broken rule answers 422 with the
reason, and nothing is saved. Unknown fields in a body are ignored.
"""

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
# Text with spaces cut off at both ends, then at least 1 character: "   " is empty.
NonEmptyText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
# Whole number bigger than 0.
AboveZero = Annotated[int, Field(gt=0)]
# 0 or bigger; "inf" and "nan" are refused (they'd be valid floats otherwise).
ZeroOrMore = Annotated[float, Field(ge=0, allow_inf_nan=False)]


class UserIn(BaseModel):
    # EmailStr checks the format (package email-validator).
    email: EmailStr
    name: NonEmptyText
    password: str = Field(min_length=8)


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    name: NonEmptyText | None = None
    password: str | None = Field(default=None, min_length=8)


# No password_hash here: it is never sent back.
class UserOut(BaseModel):
    # from_attributes: Pydantic may read a DB object (user.name), not only a dict.
    # Without it, returning a DB object fails.
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    name: str


class SpeciesIn(BaseModel):
    name: NonEmptyText
    botanical_name: NonEmptyText | None = None
    watering_interval: AboveZero
    min_dli: ZeroOrMore
    max_dli: ZeroOrMore

    # Runs after the single fields are checked: compares two fields with each other.
    @model_validator(mode="after")
    def check_dli_range(self):
        if self.min_dli > self.max_dli:
            raise ValueError("min_dli is bigger than max_dli")
        return self


# No min/max check here: maybe only one value is sent. The route compares it with
# the stored value instead (main.change_species).
class SpeciesUpdate(BaseModel):
    name: NonEmptyText | None = None
    botanical_name: NonEmptyText | None = None
    watering_interval: AboveZero | None = None
    min_dli: ZeroOrMore | None = None
    max_dli: ZeroOrMore | None = None


# Body of POST /species/lookup: just the typed name.
class SpeciesLookup(BaseModel):
    name: NonEmptyText


class SpeciesOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    botanical_name: str | None
    watering_interval: int
    max_dli: float
    min_dli: float


# No user_id: it comes from the token, so nobody can create plants for others.
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


# No plant_id: it comes from the URL (/plants/{plant_id}/events).
class CareEventIn(BaseModel):
    # Only the values of EventType are accepted, e.g. "watering".
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
