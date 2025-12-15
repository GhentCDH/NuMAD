from datetime import date
from typing import Any, List

from geoalchemy2 import Geography
from sqlmodel import Column, Field, Relationship, SQLModel


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
    name: str = Field(index=True)  # FindSpot_toponym
    site_classification: str | None = None
    archeological_structure: str | None = None
    location: Any | None = Field(
        default=None, sa_column=Column(Geography(geometry_type="POINT", srid=4326))
    )

    coins: List["Coin"] = Relationship(back_populates="find_spot")


class LocalAdminUnit(SQLModel, table=True):
    """
    Normalizes spatial data (City, Coordinates, Site Type).
    In this dataset, 'local admin-unit' acts as the primary grouping for location.
    """

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    location: Any | None = Field(
        default=None, sa_column=Column(Geography(geometry_type="POINT", srid=4326))
    )

    coins: List["Coin"] = Relationship(back_populates="find_spot")


class ObjectType(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)


class ObjectClassification(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)


class ObjectSubclass(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)


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
    local_admin_unit_id: int | None = Field(
        default=None, foreign_key="local_admin_unit.id"
    )
    object_type_id: int | None = Field(default=None, foreign_key="object_type.id")
    object_classification_id: int | None = Field(
        default=None, foreign_key="object_classification.id"
    )
    object_subclass_id: int | None = Field(
        default=None, foreign_key="object_subclass.id"
    )

    # Exact location information (coin specific)
    exact_location: str | None = None

    # Find information
    discovery_type: str | None = None
    deposition_type: str | None = None
    hoard_number: int | None = None
    chrr_link: str | None = None
    site_information: str | None = None
    context_information: str | None = None

    # Identification properties
    identification_date: date | None = Field(default=None, index=True)
    lot_code: str | None = None
    identification_unique_identifier: str | None = None
    identification_notes: str | None = None
    find_bibliography: str | None = None

    # Preservation data
    last_known_location_object: str | None = None
    cast_in_kbr: str | None = None

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
    local_admin_unit: LocalAdminUnit | None = Relationship(back_populates="coins")
    object_type: ObjectType | None = Relationship(back_populates="coins")
    object_classification: ObjectClassification | None = Relationship(
        back_populates="coins"
    )
    object_subclass: ObjectSubclass | None = Relationship(back_populates="coins")
