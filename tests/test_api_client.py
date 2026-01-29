"""Tests for Robinhood API client behavior."""

import base64

import pytest

from src.config.settings import settings
from src.api.robinhood_client import RobinhoodClient


class FakeResponse:
    def __init__(self, status_code, json_data=None, text=""):
        self.status_code = status_code
        self._json = json_data or {}
        self.text = text
        self.headers = {}

    def json(self):
        return self._json


def test_make_request_retries_on_server_error(monkeypatch, tmp_path):
    settings.data_dir = tmp_path
    settings.config_path = tmp_path / "config.json"
    monkeypatch.setenv("ROBINHOOD_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("API_KEY", "test-key")
    monkeypatch.setenv("BASE64_PRIVATE_KEY", base64.b64encode(b"\x00" * 32).decode())
    settings.reload()

    client = RobinhoodClient()

    responses = [
        FakeResponse(500, text="server error"),
        FakeResponse(200, json_data={"ok": True}),
    ]

    def fake_request(*args, **kwargs):
        return responses.pop(0)

    monkeypatch.setattr(client.session, "request", fake_request)
    monkeypatch.setattr("time.sleep", lambda *_: None)

    result = client.get_account()
    assert result == {"ok": True}
