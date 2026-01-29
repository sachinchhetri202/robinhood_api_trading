"""Centralized logging configuration."""

import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Optional


def configure_logging(
    debug: bool = False,
    log_to_file: bool = False,
    log_dir: Optional[Path] = None,
):
    """Configure root logging with optional file output."""
    level = logging.DEBUG if debug else logging.INFO
    handlers = [logging.StreamHandler()]

    if log_to_file and log_dir:
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "robinhood_trading.log"
        file_handler = TimedRotatingFileHandler(
            log_file, when="D", interval=1, backupCount=30
        )
        file_handler.setLevel(level)
        handlers.append(file_handler)

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
    )
    logging.getLogger("urllib3").setLevel(logging.DEBUG if debug else logging.WARNING)
