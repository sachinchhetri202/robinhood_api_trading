"""Tests for strategy storage and state manager."""

import os
from pathlib import Path

from src.storage.strategy_storage import StrategyStorage
from src.storage.state_manager import StateManager
from src.trading.automated_strategies import StopLossConfig, DCAConfig


def test_strategy_storage_round_trip(tmp_path):
    storage_path = tmp_path / "strategies.json"
    storage = StrategyStorage(storage_path)
    configs = {
        "stop_loss_BTC-USD": StopLossConfig(symbol="BTC-USD", stop_loss_percentage=5.0),
        "dca_ETH-USD": DCAConfig(symbol="ETH-USD", amount_per_purchase=25.0),
    }
    storage.save(configs)
    loaded = storage.load()
    assert "stop_loss_BTC-USD" in loaded
    assert "dca_ETH-USD" in loaded
    assert loaded["stop_loss_BTC-USD"].symbol == "BTC-USD"


def test_state_manager_entry_price(tmp_path):
    state_path = tmp_path / "state.json"
    manager = StateManager(state_path)
    manager.set_entry_price("BTC-USD", 50000.0)
    assert manager.get_entry_price("BTC-USD") == 50000.0
    manager.clear_entry_price("BTC-USD")
    assert manager.get_entry_price("BTC-USD") is None
