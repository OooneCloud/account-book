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


def _query_date(value, name):
    if value in (None, ""):
        return None
    try:
        parsed = date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be YYYY-MM-DD") from exc
    if parsed.isoformat() != value:
        raise ValueError(f"{name} must be YYYY-MM-DD")
    return value


def _amount(value, name):
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{name} must be a nonnegative finite number") from exc
    if not amount.is_finite() or amount < 0:
        raise ValueError(f"{name} must be a nonnegative finite number")
    return amount


def _money(value):
    return float(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def stats(args):
    """Filter inclusive ranges and aggregate by category (default) or date.

    args accepts a dict or Flask request.args. type=all adds both income and
    expense amounts; it is not a balance. Empty optional values are unrestricted.
    Category groups sort by total descending, then key; date groups sort ascending.
    """
    kind = args.get("type") or "all"
    group = args.get("group") or "category"
    if kind not in ("all", "expense", "income"):
        raise ValueError("type must be all, expense or income")
    if group not in ("category", "date"):
        raise ValueError("group must be category or date")
    start = _query_date(args.get("start"), "start")
    end = _query_date(args.get("end"), "end")
    if start and end and start > end:
        raise ValueError("start must not be after end")
    category = args.get("category")
    low = args.get("min_amount")
    high = args.get("max_amount")
    low = None if low in (None, "") else _amount(low, "min_amount")
    high = None if high in (None, "") else _amount(high, "max_amount")
    if low is not None and high is not None and low > high:
        raise ValueError("min_amount must not exceed max_amount")

    groups = {}
    total, count = Decimal("0"), 0
    for row in _load_records():
        if (kind != "all" and row["type"] != kind
                or start and row["date"] < start
                or end and row["date"] > end
                or category and row["category"] != category):
            continue
        amount = _amount(row["amount"], "record amount")
        if (low is not None and amount < low
                or high is not None and amount > high):
            continue
        key = row[group]
        subtotal, n = groups.get(key, (Decimal("0"), 0))
        groups[key] = subtotal + amount, n + 1
        total += amount
        count += 1
    ordered = sorted(groups, key=(lambda key: (-groups[key][0], key))
                     if group == "category" else (lambda key: key))
    return {"total": _money(total), "count": count,
            "items": [{"key": key, "total": _money(groups[key][0]),
                       "count": groups[key][1]} for key in ordered]}


def summary():
    """Return this calendar month's income, expense and balance in local time."""
    month = date.today().isoformat()[:7]
    income, expense = Decimal("0"), Decimal("0")
    for row in _load_records():
        if row["date"][:7] != month:
            continue
        if row["type"] == "income":
            income += _amount(row["amount"], "record amount")
        elif row["type"] == "expense":
            expense += _amount(row["amount"], "record amount")
    return {"month": month, "income": _money(income),
            "expense": _money(expense), "balance": _money(income - expense)}
