"""Symbol normalization and validation utilities."""

import re

_SYMBOL_RE = re.compile(r"^[A-Z0-9]+(-USD)?$")


def normalize_symbol_to_usd(symbol: str) -> str:
    """Normalize symbols like btc or BTC to BTC-USD."""
    normalized = symbol.strip().upper()
    if not normalized.endswith("-USD"):
        normalized = f"{normalized}-USD"
    return normalized


def validate_symbol(symbol: str) -> bool:
    """Return True if symbol matches allowed formats (e.g., BTC or BTC-USD)."""
    if not symbol:
        return False
    normalized = symbol.strip().upper()
    return bool(_SYMBOL_RE.match(normalized))
