"""Portfolio analytics utilities."""

from decimal import Decimal
from typing import Dict, List


def compute_portfolio_stats(holdings: Dict, prices: Dict, buying_power: float) -> Dict:
    """Compute high-level portfolio statistics."""
    rows: List[Dict] = []
    total_value = Decimal("0")
    for holding in holdings.get("results", []):
        asset_code = holding.get("asset_code", "UNKNOWN")
        symbol = f"{asset_code}-USD"
        quantity = Decimal(holding.get("quantity_available_for_trading", "0"))
        price = Decimal(prices.get(symbol, "0"))
        value = quantity * price
        total_value += value
        rows.append({
            "symbol": symbol,
            "quantity": quantity,
            "price": price,
            "value": value,
        })

    rows_sorted = sorted(rows, key=lambda r: r["value"], reverse=True)
    return {
        "total_value": total_value,
        "buying_power": Decimal(str(buying_power)),
        "positions": rows_sorted,
    }
