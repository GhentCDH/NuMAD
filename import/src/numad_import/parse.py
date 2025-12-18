import logging
import re
from datetime import date

from dateutil import parser as dateparser
from geoalchemy2 import WKTElement

from .model import Date

logger = logging.getLogger(__name__)


def _parse_date_p(input: str) -> date | None:
    """
    Parse dates that are formatted as `<p YYYY>` or similar
    """
    match = re.match(r"<p\s*(\d+)>", input)

    if match:
        try:
            return dateparser.parse(match.group(1))
        except Exception:
            return None


def _parse_date_slash_range(input: str) -> date | None:
    """
    Parse dates that are formatted as `YYYY/YYYY` or similar

    Note: output is the first of the two years
    """
    match = re.match(r"(\d+)/(\d+)", input)

    if match:
        try:
            return dateparser.parse(match.group(1))
        except Exception:
            return None


def _parse_date_month_range(input: str) -> date | None:
    """
    Parse dates that are formatted as `mmm.-mmm YYYY` or similar (mmm being month in natural language)

    Note: output uses the first of the two months
    """
    match = re.match(r"(\w+)\.?-(\w+)\s*(\d+)", input)

    if match:
        try:
            return dateparser.parse(f"{match.group(1)} {match.group(3)}")
        except Exception:
            return None


def _parse_date_mrt_90(input: str) -> date | None:
    """
    Parse a very specific format that was found in the data, `mrt-90`
    """
    if input == "mrt-90":
        try:
            return dateparser.parse("03-1990")
        except Exception:
            return None


def _parse_year(year: str) -> Date | None:
    if not (year_int := parse_int(year)):
        return None

    return Date(year=year_int)


def _parse_full_date(full: str) -> date | None:
    if len(full) == 0:
        return None

    try:
        return dateparser.parse(full, dayfirst=True).date()

    except Exception:
        for parser in [
            _parse_date_p,
            _parse_date_slash_range,
            _parse_date_month_range,
            _parse_date_mrt_90,
        ]:
            result = parser(full)

            if result is not None:
                return result

        logger.error(f"Failed parsing '{full}', also with custom formats")


def parse_date(full: str | None = None, year: str | None = None) -> Date | None:
    if full is None and year is None:
        return None

    assert full is not None or year is not None, (
        "parse date cannot get both a full date and a year"
    )

    if year is not None:
        return _parse_year(year)
    elif full is not None and (date := _parse_full_date(full)):
        return Date(year=date.year, month=date.month, day=date.day)

    else:
        return None


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
        clean = "".join(filter(lambda v: str.isdigit(v) or v == "-", value))
        return int(clean)
    except ValueError:
        return None


def to_location(
    longitude_field: str | None, latitude_field: str | None
) -> WKTElement | None:
    longitude = parse_float(longitude_field)
    latitude = parse_float(latitude_field)

    if longitude is None or latitude is None:
        return None

    return WKTElement(f"POINT({longitude} {latitude})", srid=4326)
