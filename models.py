"""Defines the database schema"""

from datetime import datetime
from sqlalchemy import Enum, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import enum


class Base(DeclarativeBase):
    pass


class Species(Base):
    """Defines a species."""

    __tablename__ = "species"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    watering_interval: Mapped[int] = mapped_column()
    max_dli: Mapped[float] = mapped_column()
    min_dli: Mapped[float] = mapped_column()


class Plant(Base):
    """Defines a plant."""

    __tablename__ = "plants"
    id: Mapped[int] = mapped_column(primary_key=True)
    species_id: Mapped[int] = mapped_column(ForeignKey("species.id"))
    name: Mapped[str] = mapped_column()
    location: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class EventType(enum.Enum):
    """Defines the events a CareEvent can has as a type."""

    WATERING = "watering"
    FERTILIZING = "fertilizing"
    REPOTTING = "repotting"
    HARVESTING = "harvesting"
    SOWING = "sowing"
    ACQUIRED = "acquired"
    TRIMMING = "trimming"


class CareEvent(Base):
    """Defines an event."""

    __tablename__ = "care_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    plant_id: Mapped[int] = mapped_column(ForeignKey("plants.id"))
    event_type: Mapped[EventType] = mapped_column(
        Enum(EventType, native_enum=False, length=50)
    )
    amount: Mapped[float | None] = mapped_column()
    timestamp: Mapped[datetime] = mapped_column()
