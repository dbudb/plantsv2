"""Defines the database schema"""
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Species(Base):
    __tablename__ = "species"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    watering_interval:  Mapped[int] = mapped_column()
    sunlight_preferences: Mapped[int] = mapped_column()

#class Plant(Species)