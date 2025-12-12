import logging
from typing import Type, TypeVar, Dict
from sqlmodel import SQLModel, Session, select
from src.data import get_data
from src.model import Coin, Identifier, Mint, Material, Ruler, Denomination, FindSpot
from src.db import engine
# Assuming you have a get_data function, otherwise use standard open()
# from src.data import get_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

T = TypeVar("T", bound=SQLModel)


def parse_float(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        # Replace comma with dot for European numeric formats
        return float(value.replace(",", ".").replace(" g;", "").strip())
    except ValueError:
        return None


def parse_int(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        # Remove common non-numeric chars found in dirty data
        clean = "".join(filter(str.isdigit, value))
        return int(clean)
    except ValueError:
        return None


def get_or_create_cached(
    session: Session,
    model: Type[T],
    cache: Dict[str, T],
    lookup_val: str | None,
    **kwargs,
) -> T | None:
    """
    Checks cache, then DB, then creates new instance.
    """

    if lookup_val is None:
        return None

    clean_val = lookup_val.strip()
    if clean_val in cache:
        return cache[clean_val]

    # Check DB to prevent duplication on re-runs
    statement = select(model).where(getattr(model, "name") == clean_val)
    instance = session.exec(statement).first()

    if not instance:
        instance = model(name=clean_val, **kwargs)
        session.add(instance)
        session.flush()  # Flush to generate ID
        session.refresh(instance)

    cache[clean_val] = instance
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
        "findspot": {},  # Key will be a tuple or composite string for FindSpot
    }

    reader = get_data()

    # Use encoding 'latin-1' or 'cp1252' because the sample had "Marc-AurŠle"
    # which suggests legacy Windows encoding.
    with Session(engine) as session:
        for i, row in enumerate(reader):
            try:
                # 1. Resolve Relations via Cache/DB

                ident_obj = get_or_create_cached(
                    session, Identifier, caches["identifier"], row.get("Identified by")
                )

                mint_obj = get_or_create_cached(
                    session,
                    Mint,
                    caches["mint"],
                    row.get("Mint"),
                    latitude=parse_float(row.get("Mint_latitude")),
                    longitude=parse_float(row.get("Mint_longitude")),
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

                # Special handling for FindSpot (Composite unique key logic usually needed)
                # Here simplifed to group by 'local admin-unit'
                location_name = row.get("local admin-unit")
                find_spot_obj = None
                if location_name:
                    # We treat the location name as the cache key
                    if location_name in caches["findspot"]:
                        find_spot_obj = caches["findspot"][location_name]
                    else:
                        # Check DB logic omitted for brevity, assuming simple create pattern here
                        find_spot_obj = FindSpot(
                            name=location_name,
                            toponym=row.get("FindSpot_toponym"),
                            site_classification=row.get("site_classification"),
                            latitude=parse_float(row.get("local_admin_unit_latitude")),
                            longitude=parse_float(
                                row.get("local_admin_unit_longitude")
                            ),
                        )
                        session.add(find_spot_obj)
                        session.flush()
                        caches["findspot"][location_name] = find_spot_obj

                # 2. Create Coin Object
                coin = Coin(
                    original_id=row.get("ID"),
                    jvh_id=row.get("JVH_ID"),
                    # Foreign Keys
                    identifier_id=ident_obj.id if ident_obj else None,
                    mint_id=mint_obj.id if mint_obj else None,
                    material_id=mat_obj.id if mat_obj else None,
                    ruler_id=ruler_obj.id if ruler_obj else None,
                    denomination_id=denom_obj.id if denom_obj else None,
                    find_spot_id=find_spot_obj.id if find_spot_obj else None,
                    # Metrics
                    weight=parse_float(row.get("Weight")),
                    diameter=parse_float(row.get("Diameter")),
                    die_axis=parse_int(row.get("Die axis")),
                    # Dates
                    year_start=parse_int(row.get("Object_StardDate")),
                    year_end=parse_int(row.get("ObjectEndDate")),
                    find_date=row.get("Identification_year"),  # Or Find_year
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
