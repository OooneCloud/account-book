"""Read-only reports over storage.load_records().

Records use id, date (YYYY-MM-DD), type (expense/income), category and
amount (nonnegative number). Invalid query parameters raise ValueError.
"""

from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from importlib import import_module


def _load_records():
    # Resolve at call time so the module can be imported before storage lands.
    # Missing storage is an integration error, never silently replaced by fake data.
    return import_module("storage").load_records()


def recent_records(limit=10):
    """Return newest records first, breaking date ties by numeric id."""
    if isinstance(limit, bool):
        raise ValueError("limit must be a nonnegative integer")
    if not isinstance(limit, int):
        if not isinstance(limit, str) or not limit.isascii() or not limit.isdigit():
            raise ValueError("limit must be a nonnegative integer")
        limit = int(limit)
    if limit < 0:
        raise ValueError("limit must be a nonnegative integer")
    return sorted(_load_records(),
                  key=lambda row: (row["date"], int(row["id"])),
                  reverse=True)[:limit]

