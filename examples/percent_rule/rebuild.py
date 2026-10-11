"""Synthetic rebuild of percent-button value selection (teaching fixture)."""


def apply(op: str, previous: float, current: float) -> float:
    """Return the percent *value* used for the given prior operator."""
    if op in ("+", "-"):
        return current * previous / 100.0
    if op in ("*", "/"):
        return current / 100.0
    raise ValueError(f"unsupported op: {op!r}")
