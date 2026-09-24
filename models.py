"""Defines the database schema"""

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


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
