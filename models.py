"""Defines the database schema: one class = one table, one attribute = one column.

Alembic compares these classes with the DB to write migrations
(`alembic revision --autogenerate`). `Mapped[...]` gives the column type;
`Mapped[X | None]` makes the column nullable, plain `Mapped[X]` makes it NOT NULL.
"""

from datetime import datetime
from sqlalchemy import Enum, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import enum


# Common parent of all tables. Base.metadata collects them, alembic/env.py reads it.
class Base(DeclarativeBase):
    pass


class User(Base):
    """Defines a user."""

    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    # unique: two accounts with the same email are refused by Postgres itself.
    email: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str] = mapped_column()
    # Only the hash (see auth.py). The password itself is never stored.
    password_hash: Mapped[str] = mapped_column()


class Species(Base):
    """Defines a species: what all plants of one kind need.

    Stored once per species (all tomatoes need the same), not per plant.
    """

    __tablename__ = "species"
    id: Mapped[int] = mapped_column(primary_key=True)
    # Common name, e.g. "Tomate".
    name: Mapped[str] = mapped_column()
    # e.g. "Solanum lycopersicum". Nullable: hand-made rows may have none.
    # Unique: one row per real species.
    botanical_name: Mapped[str | None] = mapped_column(unique=True)
    # Days between two waterings.
    watering_interval: Mapped[int] = mapped_column()
    # Light the species needs, as a DLI range (Daily Light Integral, mol/m²/day).
    max_dli: Mapped[float] = mapped_column()
    min_dli: Mapped[float] = mapped_column()


class Plant(Base):
    """Defines a plant: one real plant of a user."""

    __tablename__ = "plants"
    id: Mapped[int] = mapped_column(primary_key=True)
    # ForeignKey: Postgres only accepts ids that exist in the other table.
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    species_id: Mapped[int] = mapped_column(ForeignKey("species.id"))
    # Own name, e.g. "Balcony tomato": a user can have several plants of one species.
    name: Mapped[str] = mapped_column()
    location: Mapped[str] = mapped_column()
    # Set by Postgres (now()) when the row is inserted; the API never sends it.
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class EventType(enum.Enum):
    """Defines the types a CareEvent can have.

    An Enum in code instead of a table, because the code reacts to the types
    (e.g. watering → reminder later). A new type is one new line.
    """

    WATERING = "watering"
    FERTILIZING = "fertilizing"
    REPOTTING = "repotting"
    HARVESTING = "harvesting"
    # SOWING and ACQUIRED are the real start of a plant; they can be dated in the past.
    SOWING = "sowing"
    ACQUIRED = "acquired"
    TRIMMING = "trimming"


class CareEvent(Base):
    """Defines an event: something done to a plant at a time.

    All events of a plant sorted by time are its history.
    """

    __tablename__ = "care_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    plant_id: Mapped[int] = mapped_column(ForeignKey("plants.id"))
    # native_enum=False: stored as plain text (varchar 50), not as a Postgres enum
    # type. A new event type then needs no DB migration.
    event_type: Mapped[EventType] = mapped_column(
        Enum(EventType, native_enum=False, length=50)
    )
    # The type decides the unit: ml water/fertilizer, liters soil, grams harvest.
    # Empty for types without an amount (e.g. trimming).
    amount: Mapped[float | None] = mapped_column()
    # When it happened. Sent by the user, so it can lie in the past.
    timestamp: Mapped[datetime] = mapped_column()
    notes: Mapped[str | None] = mapped_column()
