from typing import List, Any
from geoalchemy2 import Geography
from sqlmodel import Column, Field, Relationship, SQLModel
from datetime import date


class Identifier(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)

    coins: List["Coin"] = Relationship(back_populates="identifier")


class Mint(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    location: Any | None = Field(
        default=None, sa_column=Column(Geography(geometry_type="POINT", srid=4326))
    )

    coins: List["Coin"] = Relationship(back_populates="mint")


class Material(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)

    coins: List["Coin"] = Relationship(back_populates="material")


class Ruler(SQLModel, table=True):
    """Represents Authority, Ruler, or Issuer."""

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    # You could add dynasty or birth/death dates here if normalized further

    coins: List["Coin"] = Relationship(back_populates="ruler")


class Denomination(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)

    coins: List["Coin"] = Relationship(back_populates="denomination")


class FindSpot(SQLModel, table=True):
    """
    Normalizes spatial data (City, Coordinates, Site Type).
    In this dataset, 'local admin-unit' acts as the primary grouping for location.
    """

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)  # local admin-unit
    toponym: str | None = None  # FindSpot_toponym
    site_classification: str | None = None
    location: Any | None = Field(
        default=None, sa_column=Column(Geography(geometry_type="POINT", srid=4326))
    )

    coins: List["Coin"] = Relationship(back_populates="find_spot")


class Coin(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    original_numers: str | None = None
    data_history: str | None = None

    # Legacy IDs (kept on the Coin record as they are specific to the object)
    original_id: str | None = Field(default=None, description="The primary ID from CSV")

    # Foreign Keys
    identifier_id: int | None = Field(default=None, foreign_key="identifier.id")
    mint_id: int | None = Field(default=None, foreign_key="mint.id")
    material_id: int | None = Field(default=None, foreign_key="material.id")
    ruler_id: int | None = Field(default=None, foreign_key="ruler.id")
    denomination_id: int | None = Field(default=None, foreign_key="denomination.id")
    find_spot_id: int | None = Field(default=None, foreign_key="findspot.id")

    # Identification properties
    identification_date: date | None = Field(default=None, index=True)

    # Physical Properties
    weight: float | None = None
    diameter: float | None = None
    die_axis: int | None = None  # Usually an integer (hours like 12, 6) or degrees

    # Dating
    year_start: int | None = None
    year_end: int | None = None
    find_date: date | None = Field(default=None, index=True)

    # Descriptions
    obverse_legend: str | None = None
    obverse_design: str | None = None
    reverse_legend: str | None = None
    reverse_design: str | None = None

    # Relationships
    identifier: Identifier | None = Relationship(back_populates="coins")
    mint: Mint | None = Relationship(back_populates="coins")
    material: Material | None = Relationship(back_populates="coins")
    ruler: Ruler | None = Relationship(back_populates="coins")
    denomination: Denomination | None = Relationship(back_populates="coins")
    find_spot: FindSpot | None = Relationship(back_populates="coins")
