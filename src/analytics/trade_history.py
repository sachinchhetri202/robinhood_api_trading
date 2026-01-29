"""Trade history formatting utilities."""

from typing import Dict, List
from tabulate import tabulate


def format_trade_history(orders: Dict) -> str:
    """Format trade history data for CLI output."""
    rows: List[List[str]] = []
    for order in orders.get("results", []):
        rows.append([
            order.get("id", "N/A"),
            order.get("symbol", "N/A"),
            order.get("side", "N/A"),
            order.get("type", "N/A"),
            order.get("state", "N/A"),
            order.get("created_at", "N/A")[:19] if order.get("created_at") else "N/A",
        ])
    if not rows:
        return "No orders found."
    return tabulate(
        rows,
        headers=["ID", "Symbol", "Side", "Type", "State", "Created"],
        tablefmt="grid",
    )
