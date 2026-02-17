from datetime import date, datetime
from typing import Any, List

from geoalchemy2 import Geography
from sqlalchemy import DateTime, func
from sqlmodel import CheckConstraint, Column, Field, Relationship, SQLModel


class Table(SQLModel):
    """Base class with common fields for all tables."""

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default=None,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"server_default": func.now(), "nullable": False},
    )
    updated_at: datetime = Field(
        default=None,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"server_default": func.now(), "nullable": False},
    )


class Identifier(Table, table=True):
    name: str = Field(index=True, unique=True)
    coins: List["Coin"] = Relationship(back_populates="identifier")


class Mint(Table, table=True):
    name: str = Field(index=True, unique=True)
    location: Any | None = Field(
        default=None, sa_column=Column(Geography(geometry_type="POINT", srid=4326))
    )
    nomisma_uri: str | None = Field(default=None, index=True)
    coins: List["Coin"] = Relationship(back_populates="mint")


class Material(Table, table=True):
    name: str = Field(index=True, unique=True)
    label: str | None = Field(default=None, index=True)
    nomisma_uri: str | None = Field(default=None, index=True)
    coins: List["Coin"] = Relationship(back_populates="material")


class CoinRuler(SQLModel, table=True):
    coin_id: int = Field(foreign_key="coin.id", primary_key=True)
    ruler_id: int = Field(foreign_key="ruler.id", primary_key=True)
    certainty: int | None = None


class Ruler(Table, table=True):
    name: str = Field(index=True, unique=True)
    start_date: int | None = Field(default=None, index=True)
    end_date: int | None = Field(default=None, index=True)
    nomisma_uri: str | None = Field(default=None, index=True)


class Denomination(Table, table=True):
    name: str = Field(index=True, unique=True)
    nomisma_uri: str | None = Field(default=None, index=True)
    coins: List["Coin"] = Relationship(back_populates="denomination")


class FindSpot(Table, table=True):
    name: str = Field(index=True)
    site_classification: str | None = None
    archeological_structure: str | None = None
    location: Any | None = Field(
        default=None, sa_column=Column(Geography(geometry_type="POINT", srid=4326))
    )
    coins: List["Coin"] = Relationship(back_populates="find_spot")


class LocalAdminUnit(Table, table=True):
    name: str = Field(index=True)
    location: Any | None = Field(
        default=None, sa_column=Column(Geography(geometry_type="POINT", srid=4326))
    )
    coins: List["Coin"] = Relationship(back_populates="local_admin_unit")


class ObjectType(Table, table=True):
    name: str = Field(unique=True)
    coins: List["Coin"] = Relationship(back_populates="object_type")


class ObjectClassification(Table, table=True):
    name: str = Field(unique=True)
    coins: List["Coin"] = Relationship(back_populates="object_classification")


class ObjectSubclass(Table, table=True):
    name: str = Field(unique=True)
    coins: List["Coin"] = Relationship(back_populates="object_subclass")


class State(Table, table=True):
    # Overwrite table name as to not conflict with Postgis' table also called `state`
    __tablename__ = "numadstate"  # type:ignore
    name: str = Field(unique=True)
    coins: List["Coin"] = Relationship(back_populates="state")


class StatedAuthority(Table, table=True):
    name: str = Field(unique=True)
    coins: List["Coin"] = Relationship(back_populates="stated_authority")


class Issuer(Table, table=True):
    name: str = Field(unique=True)
    coins: List["Coin"] = Relationship(back_populates="issuer")


class Authenticity(Table, table=True):
    name: str = Field(unique=True)
    coins: List["Coin"] = Relationship(back_populates="authenticity")


class CoinType(Table, table=True):
    name: str = Field(unique=True)


class CoinCoinType(SQLModel, table=True):
    coin_id: int = Field(foreign_key="coin.id", primary_key=True, unique=True)
    coin_type_id: int = Field(foreign_key="cointype.id", primary_key=True)
    certainty: int | None = None


class Imts(Table, table=True):
    value: int = Field(unique=True)
    coins_obv: List["Coin"] = Relationship(
        back_populates="imts_obv",
        sa_relationship_kwargs={"foreign_keys": "[Coin.imts_obv_id]"},
    )
    coins_rev: List["Coin"] = Relationship(
        back_populates="imts_rev",
        sa_relationship_kwargs={"foreign_keys": "[Coin.imts_rev_id]"},
    )


class Date(SQLModel, table=True):
    __table_args__ = (
        CheckConstraint("month >= 1 AND month <= 12", name="month range"),
        CheckConstraint("day >= 1 AND day <= 31", name="day range"),
    )

    id: int | None = Field(default=None, primary_key=True)
    year: int = Field()
    month: int | None = None
    day: int | None = None


class Coin(Table, table=True):
    original_numbers: str | None = None
    data_history: str | None = None
    original_id: str | None = Field(default=None, description="The primary ID from CSV")

    # Foreign Keys
    identifier_id: int | None = Field(default=None, foreign_key="identifier.id")
    mint_id: int | None = Field(default=None, foreign_key="mint.id")
    material_id: int | None = Field(default=None, foreign_key="material.id")
    denomination_id: int | None = Field(default=None, foreign_key="denomination.id")
    find_spot_id: int | None = Field(default=None, foreign_key="findspot.id")
    local_admin_unit_id: int | None = Field(
        default=None, foreign_key="localadminunit.id"
    )
    object_type_id: int | None = Field(default=None, foreign_key="objecttype.id")
    object_classification_id: int | None = Field(
        default=None, foreign_key="objectclassification.id"
    )
    object_subclass_id: int | None = Field(
        default=None, foreign_key="objectsubclass.id"
    )
    state_id: int | None = Field(default=None, foreign_key="numadstate.id")
    stated_authority_id: int | None = Field(
        default=None, foreign_key="statedauthority.id"
    )
    issuer_id: int | None = Field(default=None, foreign_key="issuer.id")
    authenticity_id: int | None = Field(default=None, foreign_key="authenticity.id")
    imts_obv_id: int | None = Field(default=None, foreign_key="imts.id")
    imts_rev_id: int | None = Field(default=None, foreign_key="imts.id")
    identification_date_id: int | None = Field(default=None, foreign_key="date.id")
    find_date_id: int | None = Field(default=None, foreign_key="date.id")
    object_start_id: int | None = Field(default=None, foreign_key="date.id")
    object_end_id: int | None = Field(default=None, foreign_key="date.id")

    # Exact location information
    exact_location: str | None = None

    # Find information
    discovery_type: str | None = None
    deposition_type: str | None = None
    hoard_number: int | None = None
    chrr_link: str | None = None
    site_information: str | None = None
    context_information: str | None = None

    # Identification properties
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
    die_axis: int | None = None

    # Dating
    year_start: int | None = None
    year_end: int | None = None
    reece_periods: str | None = None

    # Descriptions
    reference_work: str | None = None
    online_reference: str | None = None
    denomination_detail: str | None = None
    countermark: str | None = None
    obverse_legend: str | None = None
    obverse_design: str | None = None
    reverse_legend: str | None = None
    reverse_design: str | None = None
    object_notes: str | None = None

    # Image
    obverse_image: str | None = None
    reverse_image: str | None = None
    image_notes: str | None = None

    # Relationships
    identifier: Identifier | None = Relationship(back_populates="coins")
    mint: Mint | None = Relationship(back_populates="coins")
    material: Material | None = Relationship(back_populates="coins")
    denomination: Denomination | None = Relationship(back_populates="coins")
    find_spot: FindSpot | None = Relationship(back_populates="coins")
    local_admin_unit: LocalAdminUnit | None = Relationship(back_populates="coins")
    object_type: ObjectType | None = Relationship(back_populates="coins")
    object_classification: ObjectClassification | None = Relationship(
        back_populates="coins"
    )
    object_subclass: ObjectSubclass | None = Relationship(back_populates="coins")
    state: State | None = Relationship(back_populates="coins")
    stated_authority: StatedAuthority | None = Relationship(back_populates="coins")
    issuer: Issuer | None = Relationship(back_populates="coins")
    authenticity: Authenticity | None = Relationship(back_populates="coins")
    imts_obv: Imts | None = Relationship(
        back_populates="coins_obv",
        sa_relationship_kwargs={"foreign_keys": "[Coin.imts_obv_id]"},
    )
    imts_rev: Imts | None = Relationship(
        back_populates="coins_rev",
        sa_relationship_kwargs={"foreign_keys": "[Coin.imts_rev_id]"},
    )
    identification_date: Date | None = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Coin.identification_date_id]"}
    )
    find_date: Date | None = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Coin.find_date_id]"}
    )
    object_start: Date | None = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Coin.object_start_id]"}
    )
    object_end: Date | None = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Coin.object_end_id]"}
    )


# Persons or institutions responsible for the emission
