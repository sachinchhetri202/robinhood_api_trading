"""Configuration settings for the Robinhood client."""

import json
import os
from pathlib import Path


class Settings:
    """Settings class for Robinhood client."""

    def __init__(self):
        data_dir_env = os.getenv("ROBINHOOD_DATA_DIR")
        self.data_dir = Path(data_dir_env) if data_dir_env else Path.home() / ".robinhood_trading"
        self.config_path = self.data_dir / "config.json"
        self.reload()

    def _load_config(self) -> dict:
        default_config = {
            "api_timeout": 10,
            "retry_max": 3,
            "retry_backoff_base": 0.5,
            "retry_backoff_max": 8.0,
            "rate_limit_per_minute": 60,
            "circuit_breaker_threshold": 5,
            "circuit_breaker_timeout": 60,
            "log_to_file": False,
        }
        try:
            if not self.config_path.exists():
                self.data_dir.mkdir(parents=True, exist_ok=True)
                with self.config_path.open("w", encoding="utf-8") as handle:
                    json.dump(default_config, handle, indent=2)
                return default_config
            with self.config_path.open("r", encoding="utf-8") as handle:
                stored = json.load(handle)
            merged = {**default_config, **stored}
            return merged
        except (OSError, PermissionError):
            return default_config

    def reload(self):
        """Reload settings from env and config."""
        config = self._load_config()
        self.API_KEY = os.getenv("API_KEY")
        self.BASE64_PRIVATE_KEY = os.getenv("BASE64_PRIVATE_KEY")
        base_url = os.getenv("ROBINHOOD_API_BASE_URL", "https://trading.robinhood.com")
        # Normalize base URL - remove trailing slashes
        base_url = base_url.rstrip("/")
        
        # Auto-fix common mistakes for backward compatibility
        if base_url == "https://api.robinhood.com/crypto":
            # Old format that was used - automatically fix it
            base_url = "https://trading.robinhood.com"
        elif base_url == "https://api.robinhood.com":
            # Another old format - fix it
            base_url = "https://trading.robinhood.com"
        elif "/crypto" in base_url and "trading.robinhood.com" not in base_url:
            # Remove /crypto suffix if present (endpoints already include it)
            base_url = base_url.replace("/crypto", "").rstrip("/")
            if base_url == "https://api.robinhood.com":
                base_url = "https://trading.robinhood.com"
        
        # Warn if still using incorrect base URL
        if "api.robinhood.com" in base_url and "trading.robinhood.com" not in base_url:
            import warnings
            warnings.warn(
                f"Warning: ROBINHOOD_API_BASE_URL appears incorrect: '{base_url}'.\n"
                f"The correct base URL should be 'https://trading.robinhood.com'.\n"
                f"Please update your .env file.",
                UserWarning
            )
        self.ROBINHOOD_API_BASE_URL = base_url
        self.API_TIMEOUT = int(config["api_timeout"])
        self.RETRY_MAX = int(config["retry_max"])
        self.RETRY_BACKOFF_BASE = float(config["retry_backoff_base"])
        self.RETRY_BACKOFF_MAX = float(config["retry_backoff_max"])
        self.RATE_LIMIT_PER_MINUTE = int(config["rate_limit_per_minute"])
        self.CIRCUIT_BREAKER_THRESHOLD = int(config["circuit_breaker_threshold"])
        self.CIRCUIT_BREAKER_TIMEOUT = int(config["circuit_breaker_timeout"])
        self.LOG_TO_FILE = bool(config["log_to_file"])
        self.LOG_DIR = self.data_dir / "logs"
        self.STRATEGY_PATH = self.data_dir / "strategies.json"
        self.STATE_PATH = self.data_dir / "state.json"

    def validate(self) -> bool:
        """Validate required settings are present."""
        return bool(self.API_KEY and self.BASE64_PRIVATE_KEY)


# Global settings instance
settings = Settings()