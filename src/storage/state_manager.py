"""Persist runtime strategy state to disk."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


class StateManager:
    """Track entry prices and DCA purchase state."""

    def __init__(self, state_path: Path):
        self.state_path = state_path
        self._state: Dict = {"entry_prices": {}, "dca": {}}
        self._load()

    def _load(self):
        if not self.state_path.exists():
            return
        try:
            with self.state_path.open("r", encoding="utf-8") as handle:
                self._state = json.load(handle)
        except (OSError, json.JSONDecodeError):
            self._state = {"entry_prices": {}, "dca": {}}

    def _save(self):
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        with self.state_path.open("w", encoding="utf-8") as handle:
            json.dump(self._state, handle, indent=2)

    def get_entry_price(self, symbol: str) -> Optional[float]:
        value = self._state.get("entry_prices", {}).get(symbol)
        return float(value) if value is not None else None

    def set_entry_price(self, symbol: str, price: float):
        self._state.setdefault("entry_prices", {})[symbol] = price
        self._save()

    def clear_entry_price(self, symbol: str):
        self._state.setdefault("entry_prices", {}).pop(symbol, None)
        self._save()

    def get_dca_state(self, symbol: str) -> Dict:
        return self._state.get("dca", {}).get(symbol, {})

    def update_dca_state(self, symbol: str, last_purchase_at: Optional[datetime], purchase_count: int):
        record = {
            "last_purchase_at": last_purchase_at.isoformat() if last_purchase_at else None,
            "purchase_count": purchase_count,
        }
        self._state.setdefault("dca", {})[symbol] = record
        self._save()
