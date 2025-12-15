import logging
from typing import Dict, Type, TypeVar

from rich.logging import RichHandler
from sqlmodel import Session, SQLModel, select

from src.data import get_data
from src.db import engine
from src.model import (
    Coin,
    CoinRuler,
    Denomination,
    FindSpot,
    Identifier,
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
from src.parse import parse_date, parse_float, parse_int, to_location

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


def get_id(obj: Table | None) -> int | None:
    return obj.id if obj else None


def get_or_create(
    session: Session,
    model: Type[T],
    cache: Dict[str, T],
    name: str | None,
    **kwargs,
) -> T | None:
    """Checks cache, then DB, then creates new instance."""
    if not name or not (clean_name := name.strip()):
        return None

    if clean_name in cache:
        return cache[clean_name]

    assert hasattr(model, "name"), (
        f"the cached model {model.__class__} should have a column 'name'"
    )

    statement = select(model).where(model.name == clean_name)  # pyright:ignore
    if instance := session.exec(statement).first():
        cache[clean_name] = instance
        return instance

    instance = model(name=clean_name, **kwargs)
    session.add(instance)
    session.flush()
    cache[clean_name] = instance
    return instance


def create_coin(row: dict, relations: dict[str, Table | None]) -> Coin:
    """Create a Coin instance from a row and resolved relations."""
    return Coin(
        original_id=row.get("ID"),
        # Foreign keys
        identifier_id=get_id(relations["identifier"]),
        mint_id=get_id(relations["mint"]),
        material_id=get_id(relations["material"]),
        denomination_id=get_id(relations["denomination"]),
        find_spot_id=get_id(relations["find_spot"]),
        local_admin_unit_id=get_id(relations["local_admin_unit"]),
        object_type_id=get_id(relations["object_type"]),
        object_classification_id=get_id(relations["object_classification"]),
        object_subclass_id=get_id(relations["object_subclass"]),
        state_id=get_id(relations["state"]),
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
        identification_date=parse_date(row.get("Identification_year")),
        lot_code=row.get("Lot_Code"),
        identification_unique_identifier=row.get("unique_identifier"),
        identification_notes=row.get("identification_notes"),
        # Preservation
        last_known_location_object=row.get("last_known_location_object"),
        cast_in_kbr=row.get("Cast in KBR"),
        # Metrics
        weight=parse_float(row.get("Weight")),
        diameter=parse_float(row.get("Diameter")),
        die_axis=parse_int(row.get("Die axis")),
        # Dates
        year_start=parse_int(row.get("Object_StartDate")),
        year_end=parse_int(row.get("ObjectEndDate")),
        find_date=parse_date(row.get("Find_year")),
        reece_periods=row.get("Periods (Reece adapted)"),
        # Descriptions
        obverse_legend=row.get("Obverse_legend"),
        obverse_design=row.get("Obverse_design"),
        reverse_legend=row.get("Reverse_legend"),
        reverse_design=row.get("Reverse_design"),
    )


def main():
    SQLModel.metadata.create_all(engine)

    caches: dict[str, dict] = {
        "identifier": {},
        "mint": {},
        "material": {},
        "ruler": {},
        "denomination": {},
        "find_spot": {},
        "local_admin_unit": {},
        "object_type": {},
        "object_classification": {},
        "object_subclass": {},
        "state": {},
        "stated_authority": {},
    }

    with Session(engine) as session:
        for i, row in enumerate(get_data()):
            try:
                relations = {
                    "identifier": get_or_create(
                        session,
                        Identifier,
                        caches["identifier"],
                        row.get("Identified by"),
                    ),
                    "mint": get_or_create(
                        session,
                        Mint,
                        caches["mint"],
                        row.get("Mint"),
                        location=to_location(
                            row.get("Mint_longitude"), row.get("Mint_latitude")
                        ),
                    ),
                    "material": get_or_create(
                        session, Material, caches["material"], row.get("Material")
                    ),
                    "ruler": get_or_create(
                        session,
                        Ruler,
                        caches["ruler"],
                        row.get("Ruler"),
                        start_date=parse_date(row.get("Ruler_startDate")),
                        end_date=parse_date(row.get("Ruler_endDate")),
                    ),
                    "denomination": get_or_create(
                        session,
                        Denomination,
                        caches["denomination"],
                        row.get("Denomination"),
                    ),
                    "object_type": get_or_create(
                        session,
                        ObjectType,
                        caches["object_type"],
                        row.get("Object_type"),
                    ),
                    "object_classification": get_or_create(
                        session,
                        ObjectClassification,
                        caches["object_classification"],
                        row.get("Object_classification"),
                    ),
                    "object_subclass": get_or_create(
                        session,
                        ObjectSubclass,
                        caches["object_subclass"],
                        row.get("Object_subclass"),
                    ),
                    "find_spot": get_or_create(
                        session,
                        FindSpot,
                        caches["find_spot"],
                        row.get("FindSpot_toponym"),
                        site_classification=row.get("site_classification"),
                        archeological_structure=row.get("archeological_structure"),
                        location=to_location(
                            row.get("FindSpot_longitude"), row.get("FindSpot_latitude")
                        ),
                    ),
                    "local_admin_unit": get_or_create(
                        session,
                        LocalAdminUnit,
                        caches["local_admin_unit"],
                        row.get("local admin-unit"),
                        location=to_location(
                            row.get("local_admin_unit_longitude"),
                            row.get("local_admin_unit_latitude"),
                        ),
                    ),
                    "state": get_or_create(
                        session,
                        State,
                        caches["state"],
                        row.get("State"),
                    ),
                    "stated_authority": get_or_create(
                        session,
                        StatedAuthority,
                        caches["stated_authority"],
                        row.get("StatedAuthority"),
                    ),
                }

                session.add(coin := create_coin(row, relations))
                session.flush()

                if (ruler := relations["ruler"]) and coin.id is not None:
                    session.add(
                        CoinRuler(
                            coin_id=coin.id,
                            ruler_id=ruler.id,
                            certainty=parse_int(row.get("Ruler_certainty_attribute")),
                        )
                    )

                if i % 100 == 0:
                    logger.info(f"Processed {i} rows...")
                    session.commit()

            except Exception as e:
                logger.error(f"Failed row {i} (ID: {row.get('ID')}): {e}")
                continue

        session.commit()
        logger.info("Import complete.")


if __name__ == "__main__":
    main()
