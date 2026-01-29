"""Persist strategy configurations to disk."""

import json
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from src.trading.automated_strategies import StrategyConfig


class StrategyStorage:
    """Simple JSON storage for strategy configs."""

    def __init__(self, storage_path: Path):
        self.storage_path = storage_path

    def load(self) -> Dict[str, "StrategyConfig"]:
        if not self.storage_path.exists():
            return {}
        try:
            with self.storage_path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (OSError, json.JSONDecodeError):
            return {}
        strategies: Dict[str, "StrategyConfig"] = {}
        for item in data.get("strategies", []):
            strategy_type = item.pop("strategy_type", "")
            from src.trading.automated_strategies import StopLossConfig, DCAConfig, TrailingStopConfig
            if strategy_type == "stop_loss":
                config = StopLossConfig(**item)
            elif strategy_type == "dca":
                config = DCAConfig(**item)
            elif strategy_type == "trailing_stop":
                config = TrailingStopConfig(**item)
            else:
                continue
            key = f"{strategy_type}_{config.symbol}"
            strategies[key] = config
        return strategies

    def save(self, configs: Dict[str, "StrategyConfig"]):
        payload: List[Dict] = []
        for key, config in configs.items():
            config_dict = asdict(config)
            if key.startswith("stop_loss"):
                config_dict["strategy_type"] = "stop_loss"
            elif key.startswith("dca"):
                config_dict["strategy_type"] = "dca"
            elif key.startswith("trailing_stop"):
                config_dict["strategy_type"] = "trailing_stop"
            else:
                continue
            payload.append(config_dict)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with self.storage_path.open("w", encoding="utf-8") as handle:
            json.dump({"strategies": payload}, handle, indent=2)
