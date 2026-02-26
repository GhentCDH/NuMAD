import logging
from typing import Dict, Type, TypeVar

from rich.logging import RichHandler
from sqlmodel import Session, SQLModel, select

from .data import get_data
from .db import create_updated_at_trigger, engine
from .util import get_nomisma_ruler, get_nomisma_mint, get_nomisma_denomination, get_nomisma_material, \
    fix_online_reference
from .model import (
    Authenticity,
    Coin,
    CoinCoinType,
    CoinRuler,
    CoinType,
    Date,
    Denomination,
    FindSpot,
    Identifier,
    Imts,
    Issuer,
    LocalAdminUnit,
    Material,
    Mint,
    ObjectClassification,
    ObjectSubclass,
    ObjectType,
    Ruler,
    State,
    StatedAuthority,
    Table,
)
from .parse import parse_date, parse_float, parse_int, to_location

handler = RichHandler(
    rich_tracebacks=True,
    tracebacks_show_locals=True,
    markup=True,
    show_time=True,
    show_path=True,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[handler],
)

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=SQLModel)


def get_id(obj: Table | Date | None) -> int | None:
    return obj.id if obj else None


def get_or_create(
    session: Session,
    model: Type[T],
    cache: Dict[str, T],
    **kwargs,
) -> T | None:
    """Checks cache, then DB, then creates new instance."""

    if (key_col := next(iter(kwargs))) is None:
        return None

    key_col_val = kwargs.get(key_col)
    if not key_col_val:
        return None

    if not (
        clean_val := key_col_val.strip() if type(key_col_val) is str else key_col_val
    ):
        return None

    if clean_val in cache:
        return cache[clean_val]

    assert hasattr(model, key_col), (
        f"the cached model {model.__class__} should have a column '{key_col}'"
    )

    statement = select(model).where(getattr(model, key_col) == clean_val)  # type:ignore
    if instance := session.exec(statement).first():
        cache[clean_val] = instance
        return instance

    kwargs.update({key_col: clean_val})

    instance = model(**kwargs)
    session.add(instance)
    session.flush()
    cache[clean_val] = instance
    return instance


def get_or_create_date(
    session: Session,
    cache: Dict[tuple[int, int | None, int | None], Date],
    date: Date | None,
) -> Date | None:
    """Get or create a Date instance, using (year, month, day) as composite key."""
    if date is None:
        return None

    key = (date.year, date.month, date.day)

    if key in cache:
        return cache[key]

    statement = select(Date).where(
        Date.year == date.year,
        Date.month == date.month if date.month is not None else Date.month.is_(None),  # type:ignore
        Date.day == date.day if date.day is not None else Date.day.is_(None),  # type:ignore
    )

    if instance := session.exec(statement).first():
        cache[key] = instance
        return instance

    instance = Date(year=date.year, month=date.month, day=date.day)
    session.add(instance)
    session.flush()
    cache[key] = instance
    return instance


def create_coin(row: dict, relations: dict[str, Table | Date | None]) -> Coin:
    """Create a Coin instance from a row and resolved relations."""
    return Coin(
        original_id=row.get("ID"),
        original_numbers=row.get("Original numbers"),
        data_history=row.get("Data history"),
        # Foreign keys
        authenticity_id=get_id(relations["authenticity"]),
        denomination_id=get_id(relations["denomination"]),
        find_spot_id=get_id(relations["find_spot"]),
        identifier_id=get_id(relations["identifier"]),
        imts_obv_id=get_id(relations["imts_obv"]),
        imts_rev_id=get_id(relations["imts_rev"]),
        issuer_id=get_id(relations["issuer"]),
        local_admin_unit_id=get_id(relations["local_admin_unit"]),
        material_id=get_id(relations["material"]),
        mint_id=get_id(relations["mint"]),
        object_classification_id=get_id(relations["object_classification"]),
        object_subclass_id=get_id(relations["object_subclass"]),
        object_type_id=get_id(relations["object_type"]),
        state_id=get_id(relations["state"]),
        stated_authority_id=get_id(relations["stated_authority"]),
        identification_date_id=get_id(relations["identification_date"]),
        find_date_id=get_id(relations["find_date"]),
        object_start_id=get_id(relations["object_start"]),
        object_end_id=get_id(relations["object_end"]),
        # Location
        exact_location=row.get("exact_location"),
        # Find information
        discovery_type=row.get("DiscoveryType"),
        deposition_type=row.get("DepositionType"),
        hoard_number=parse_int(row.get("Hoard_number")),
        chrr_link=row.get("CHRR_link"),
        site_information=row.get("Site_information"),
        context_information=row.get("Context_information"),
        find_bibliography=row.get("Find_bibliography"),
        # Identification
        lot_code=row.get("Lot_Code"),
        identification_unique_identifier=row.get("unique_identifier"),
        identification_notes=row.get("identification_notes"),
        # Preservation
        last_known_location_object=row.get("last_known_location_object"),
        cast_in_kbr=row.get("Cast in KBR"),
        # Metrics
        weight=parse_float(row.get("Weight ")),
        diameter=parse_float(row.get("Diameter")),
        die_axis=parse_int(row.get("Die axis")),
        # Dates
        year_start=parse_int(row.get("Object_StardDate")),
        year_end=parse_int(row.get("ObjectEndDate")),
        reece_periods=row.get("Periods (Reece adapted)"),
        # Descriptions
        reference_work=row.get("ReferenceWork"),
        online_reference=fix_online_reference(row.get("Online reference")),
        denomination_detail=row.get("Den_detail"),
        countermark=row.get("Countermark"),
        obverse_legend=row.get("Obverse_legend"),
        obverse_design=row.get("Obverse_design"),
        reverse_legend=row.get("Reverse_legend"),
        reverse_design=row.get("Reverse_design"),
        object_notes=row.get("Object_notes"),
        obverse_image=row.get("Foto obv."),
        reverse_image=row.get("Foto rev."),
        image_notes=row.get("Foto notes"),
    )


def main():
    SQLModel.metadata.create_all(engine)
    create_updated_at_trigger(engine)

    caches: dict[str, dict] = {
        "authenticity": {},
        "coin_type": {},
        "date": {},  # This one uses tuple keys: (year, month, day)
        "denomination": {},
        "find_spot": {},
        "identifier": {},
        "imts": {},
        "issuer": {},
        "local_admin_unit": {},
        "material": {},
        "mint": {},
        "object_classification": {},
        "object_subclass": {},
        "object_type": {},
        "ruler": {},
        "state": {},
        "stated_authority": {},
    }

    with Session(engine) as session:
        for i, row in enumerate(get_data()):
            try:
                relations = {
                    "authenticity": get_or_create(
                        session,
                        Authenticity,
                        caches["authenticity"],
                        name=row.get("Authenticity"),
                    ),
                    "coin_type": get_or_create(
                        session, CoinType, caches["coin_type"], name=row.get("Type")
                    ),
                    "denomination": get_or_create(
                        session,
                        Denomination,
                        caches["denomination"],
                        name=row.get("Denomination"),
                    ),
                    "find_spot": get_or_create(
                        session,
                        FindSpot,
                        caches["find_spot"],
                        name=row.get("FindSpot_toponym"),
                        site_classification=row.get("site_classification"),
                        archeological_structure=row.get("archeological_structure"),
                        location=to_location(
                            row.get("FindSpot_longitude"), row.get("FindSpot_latitude")
                        ),
                    ),
                    "identifier": get_or_create(
                        session,
                        Identifier,
                        caches["identifier"],
                        name=row.get("Identified by"),
                    ),
                    "identification_date": get_or_create_date(
                        session,
                        caches["date"],
                        parse_date(row.get("Identification_year")),
                    ),
                    "find_date": get_or_create_date(
                        session, caches["date"], parse_date(year=row.get("Find_year"))
                    ),
                    "object_start": get_or_create_date(
                        session,
                        caches["date"],
                        parse_date(year=row.get("Object_StardDate")),
                    ),
                    "object_end": get_or_create_date(
                        session,
                        caches["date"],
                        parse_date(year=row.get("ObjectEndDate")),
                    ),
                    "imts_obv": get_or_create(
                        session,
                        Imts,
                        caches["imts"],
                        value=parse_int(row.get("IMTS-obv")),
                    ),
                    "imts_rev": get_or_create(
                        session,
                        Imts,
                        caches["imts"],
                        value=parse_int(row.get("IMTS-rev")),
                    ),
                    "issuer": get_or_create(
                        session,
                        Issuer,
                        caches["issuer"],
                        name=row.get("Issuer"),
                    ),
                    "local_admin_unit": get_or_create(
                        session,
                        LocalAdminUnit,
                        caches["local_admin_unit"],
                        name=row.get("local admin-unit"),
                        location=to_location(
                            row.get("local_admin_unit_longitude"),
                            row.get("local_admin_unit_latitude"),
                        ),
                    ),
                    "material": get_or_create(
                        session, Material, caches["material"], name=row.get("Material")
                    ),
                    "mint": get_or_create(
                        session,
                        Mint,
                        caches["mint"],
                        name=row.get("Mint"),
                        location=to_location(
                            row.get("Mint_longitude"), row.get("Mint_latitude")
                        ),
                    ),
                    "object_classification": get_or_create(
                        session,
                        ObjectClassification,
                        caches["object_classification"],
                        name=row.get("Object_classification"),
                    ),
                    "object_subclass": get_or_create(
                        session,
                        ObjectSubclass,
                        caches["object_subclass"],
                        name=row.get("Object_subclass"),
                    ),
                    "object_type": get_or_create(
                        session,
                        ObjectType,
                        caches["object_type"],
                        name=row.get("Object_type"),
                    ),
                    "ruler": get_or_create(
                        session,
                        Ruler,
                        caches["ruler"],
                        name=row.get("Ruler"),
                        start_date=parse_int(row.get("Ruler_StartDate")),
                        end_date=parse_int(row.get("Ruler_EndDate")),
                    ),
                    "state": get_or_create(
                        session,
                        State,
                        caches["state"],
                        name=row.get("State"),
                    ),
                    "stated_authority": get_or_create(
                        session,
                        StatedAuthority,
                        caches["stated_authority"],
                        name=row.get("StatedAuthority"),
                    ),
                }

                session.add(coin := create_coin(row, relations))
                session.flush()

                # Adding M-N relations later because they require knowing `coin.id`

                if (ruler := relations["ruler"]) and coin.id is not None:
                    session.add(
                        CoinRuler(
                            coin_id=coin.id,
                            ruler_id=ruler.id,
                            certainty=parse_int(row.get("Ruler_certainty_attribute")),
                        )
                    )

                if (coin_type := relations["coin_type"]) and coin.id is not None:
                    session.add(
                        CoinCoinType(
                            coin_id=coin.id,
                            coin_type_id=coin_type.id,
                            certainty=parse_int(row.get("type_certainty_attribute")),
                        )
                    )

                if i % 100 == 0:
                    logger.info(f"Processed {i} rows...")
                    session.commit()

            except Exception as e:
                logger.error(f"Failed row {i} (ID: {row.get('ID')}): {e}")
                continue

        session.commit()

        logger.info(f"\nProcessing rulers URIs")
        rulers = session.exec(select(Ruler)).all()
        for i, ruler in enumerate(rulers):
            if ruler.nomisma_uri is None:
                ruler.nomisma_uri = get_nomisma_ruler(
                    ruler.name,
                    ruler.start_date,
                    ruler.end_date,
                )
            if i % 10 == 0:
                logger.info(f"Processed {i} rulers...")
        session.commit()

        logger.info(f"\nProcessing mints URIs")
        mints = session.exec(select(Mint)).all()
        for i, mint in enumerate(mints):
            if mint.nomisma_uri is None:
                mint.nomisma_uri = get_nomisma_mint(
                    mint.name
                )
            if i % 10 == 0:
                logger.info(f"Processed {i} mints...")
        session.commit()

        logger.info(f"\nProcessing denominations URIs")
        denoms = session.exec(select(Denomination)).all()
        for i, denom in enumerate(denoms):
            if denom.nomisma_uri is None:
                denom.nomisma_uri = get_nomisma_denomination(
                    denom.name
                )
            if i % 10 == 0:
                logger.info(f"Processed {i} denominations...")
        session.commit()

        logger.info(f"\nProcessing material URIs")
        materials = session.exec(select(Material)).all()
        for i, material in enumerate(materials):
            if material.nomisma_uri is None:
                nomisma_material = get_nomisma_material(material.name)
                if nomisma_material is not None:
                    material.nomisma_uri = nomisma_material["nmo"]
                    material.label = nomisma_material["label"]
                else :
                    material.label = material.name

        session.commit()

        logger.info("Import complete.")


def erd():
    import subprocess

    from .config import DB_STRING

    subprocess.run(["eralchemy", "-i", DB_STRING, "-s", "public", "-o", "erd.md"])

    subprocess.run(["sed", "-i", "s/public_//g", "erd.md"])
    subprocess.run(
        ["sed", "-i", "-e", "/^<!--$/d", "-e", "/^-->$/d", "-e", r"/!\[\]/d", "erd.md"]
    )
    subprocess.run(["mv", "erd.md", "erd.mermaid"])
