import csv
from typing import Any

from .config import CSV, PERIODS_CSV


def get_data() -> list[dict[str, Any]]:
    with open(CSV, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        data = list(reader)

    return data


def get_periods() -> list[dict[str, Any]]:
    with open(PERIODS_CSV, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        return list(reader)
