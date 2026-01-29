"""Tests for automated strategies."""

import base64

from src.config.settings import settings
from src.trading.automated_strategies import AutomatedTradingBot, DCAConfig


def test_strategy_persistence(monkeypatch, tmp_path):
    monkeypatch.setenv("ROBINHOOD_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("API_KEY", "test-key")
    monkeypatch.setenv("BASE64_PRIVATE_KEY", base64.b64encode(b"\x00" * 32).decode())
    settings.reload()

    bot = AutomatedTradingBot()
    config = DCAConfig(symbol="BTC-USD", amount_per_purchase=10.0)
    bot.add_dca_strategy(config)

    new_bot = AutomatedTradingBot()
    new_bot.load_strategies()
    strategies = new_bot.list_strategies()
    assert "dca_BTC-USD" in strategies
