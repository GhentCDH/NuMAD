import logging
from typing import Dict, Type, TypeVar

from sqlmodel import Session, SQLModel, select

from src.data import get_data
from src.db import engine
from src.model import (
    Coin,
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
)
from src.parse import parse_date, parse_float, parse_int, to_location

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

T = TypeVar("T", bound=SQLModel)


def get_or_create_cached(
    session: Session,
    model: Type[T],
    cache: Dict[str, T],
    name: str | None,
    **kwargs,
) -> T | None:
    """
    Checks cache, then DB, then creates new instance.
    """

    if name is None:
        return None

    clean_name = name.strip()
    if len(name) == 0:
        return None

    if clean_name in cache:
        return cache[clean_name]

    # Check DB to prevent duplication on re-runs
    statement = select(model).where(getattr(model, "name") == clean_name)
    instance = session.exec(statement).first()

    if not instance:
        instance = model(name=clean_name, **kwargs)
        session.add(instance)
        session.flush()  # Flush to generate ID
        session.refresh(instance)

    cache[clean_name] = instance
    return instance


def main():
    SQLModel.metadata.create_all(engine)

    # In-memory caches to reduce DB roundtrips
    # Key = Name, Value = Model Instance
    caches = {
        "identifier": {},
        "mint": {},
        "material": {},
        "ruler": {},
        "denomination": {},
        "findspot": {},
        "lau": {},
        "object_type": {},
    }

    reader = get_data()

    with Session(engine) as session:
        for i, row in enumerate(reader):
            # if i == 5000:
            #     break

            try:
                # 1. Resolve Relations via Cache/DB

                ident_obj = get_or_create_cached(
                    session, Identifier, caches["identifier"], row.get("Identified by")
                )

                location = to_location(row["Mint_longitude"], row["Mint_latitude"])

                mint_obj = get_or_create_cached(
                    session, Mint, caches["mint"], row.get("Mint"), location=location
                )

                mat_obj = get_or_create_cached(
                    session, Material, caches["material"], row.get("Material")
                )

                # "Ruler" column seems to be the primary authority
                ruler_obj = get_or_create_cached(
                    session, Ruler, caches["ruler"], row.get("Ruler")
                )

                denom_obj = get_or_create_cached(
                    session,
                    Denomination,
                    caches["denomination"],
                    row.get("Denomination"),
                )

                object_type_obj = get_or_create_cached(
                    session, ObjectType, caches["object_type"], row.get("Object_type")
                )

                object_classification_obj = get_or_create_cached(
                    session,
                    ObjectClassification,
                    caches["object_classification"],
                    row.get("Object_classification"),
                )

                object_subclass_obj = get_or_create_cached(
                    session,
                    ObjectSubclass,
                    caches["object_subclass"],
                    row.get("Object_subclass"),
                )

                # Special handling for FindSpot (Composite unique key logic usually needed)
                findspot_topo = row.get("FindSpot_toponym")
                findspot_obj = None
                if findspot_topo:
                    # TODO: if the row that's used to create this FindSpot doesn't contain
                    #       any of the fields required (site_classification, location, archeological_structure),
                    #       but another row with the same findspot name does,
                    #       The entry in the database should be updated with the information that the new row
                    #       with the same findspot name adds

                    # We treat the location name as the cache key
                    if findspot_topo in caches["findspot"]:
                        findspot_obj = caches["findspot"][findspot_topo]
                    else:
                        # Check DB logic omitted for brevity, assuming simple create pattern here
                        location = to_location(
                            row["FindSpot_longitude"],
                            row["FindSpot_latitude"],
                        )
                        findspot_obj = FindSpot(
                            name=findspot_topo,
                            site_classification=row.get("site_classification"),
                            archeological_structure=row.get("archeological_structure"),
                            location=location,
                        )
                        session.add(findspot_obj)
                        session.flush()
                        caches["findspot"][findspot_topo] = findspot_obj

                # Special handling for Local Admin Unit columns
                location_name = row.get("local admin-unit")
                local_admin_unit_obj = None
                if location_name:
                    # We treat the location name as the cache key
                    if location_name in caches["lau"]:
                        local_admin_unit_obj = caches["lau"][location_name]
                    else:
                        # Check DB logic omitted for brevity, assuming simple create pattern here
                        location = to_location(
                            row["local_admin_unit_longitude"],
                            row["local_admin_unit_latitude"],
                        )
                        local_admin_unit_obj = LocalAdminUnit(
                            name=location_name,
                            location=location,
                        )
                        session.add(local_admin_unit_obj)
                        session.flush()
                        caches["lau"][location_name] = local_admin_unit_obj

                # 2. Create Coin Object
                coin = Coin(
                    original_id=row.get("ID"),
                    # Foreign Keys
                    identifier_id=ident_obj.id if ident_obj else None,
                    mint_id=mint_obj.id if mint_obj else None,
                    material_id=mat_obj.id if mat_obj else None,
                    ruler_id=ruler_obj.id if ruler_obj else None,
                    denomination_id=denom_obj.id if denom_obj else None,
                    find_spot_id=findspot_obj.id if findspot_obj else None,
                    # Exact location information (unstructured string)
                    exact_location=row.get("exact_location"),
                    # Find information
                    discovery_type=row.get("DiscoveryType"),
                    deposition_type=row.get("DepositionType"),
                    hoard_number=parse_int(row.get("Hoard_number")),
                    chrr_link=row.get("CHRR_link"),
                    site_information=row.get("Site_information"),
                    context_information=row.get("Context_information"),
                    find_bibliography=row.get("Find_bibliography"),
                    # Identification information
                    identification_date=parse_date(row.get("Identification_year")),
                    lot_code=row.get("Lot_Code"),
                    identification_unique_identifier=row.get("unique_identifier"),
                    identification_notes=row.get("identification_notes"),
                    # Preservation data
                    last_known_location_object=row.get("last_known_location_object"),
                    cast_in_kbr=row.get("Cast in KBR"),
                    # Object classification
                    object_type_id=object_type_obj.id if object_type_obj else None,
                    object_classification_id=object_classification_obj.id
                    if object_classification_obj
                    else None,
                    object_subclass_id=object_subclass_obj.id
                    if object_subclass_obj
                    else None,
                    # Metrics
                    weight=parse_float(row.get("Weight")),
                    diameter=parse_float(row.get("Diameter")),
                    die_axis=parse_int(row.get("Die axis")),
                    # Dates
                    year_start=parse_int(row.get("Object_StardDate")),
                    year_end=parse_int(row.get("ObjectEndDate")),
                    find_date=parse_date(row.get("Find_year")),
                    # Descriptions
                    obverse_legend=row.get("Obverse_legend"),
                    obverse_design=row.get("Obverse_design"),
                    reverse_legend=row.get("Reverse_legend"),
                    reverse_design=row.get("Reverse_design"),
                )

                session.add(coin)

                if i % 100 == 0:
                    print(f"Processed {i} rows...")
                    session.commit()  # Commit in chunks

            except Exception as e:
                logger.error(f"Failed row {i} (ID: {row.get('ID')}): {e}")
                # Continue to next row despite error
                continue

        session.commit()
        print("Import complete.")


if __name__ == "__main__":
    main()
