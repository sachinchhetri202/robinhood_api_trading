#!/usr/bin/env python3
"""
Build a compressed .pyz (zipapp) for the CLI.

Usage:
  python scripts/build_zipapp.py
"""

import shutil
import sys
import tempfile
import zipapp
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DIST_DIR = PROJECT_ROOT / "dist"
OUTPUT_FILE = DIST_DIR / "robinhood_cli.pyz"

INCLUDE_DIRS = {"src"}
INCLUDE_FILES = {"main.py", "generate_keypair.py", "README.md", "requirements.txt"}
EXCLUDE_DIRS = {".git", ".idea", ".vscode", "__pycache__", "venv", "env", "tests", "docs", "dist"}


def should_include(path: Path) -> bool:
    if any(part in EXCLUDE_DIRS for part in path.parts):
        return False
    if path.is_dir():
        return path.name in INCLUDE_DIRS
    return path.name in INCLUDE_FILES or any(part in INCLUDE_DIRS for part in path.parts)


def main() -> int:
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    if OUTPUT_FILE.exists():
        OUTPUT_FILE.unlink()

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_root = Path(tmp_dir)
        for item in PROJECT_ROOT.iterdir():
            if not should_include(item):
                continue
            dest = tmp_root / item.name
            if item.is_dir():
                shutil.copytree(item, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dest)

        zipapp.create_archive(
            tmp_root,
            OUTPUT_FILE,
            main="main:cli",
            interpreter="/usr/bin/env python3",
            compressed=True,
        )

    print(f"Created: {OUTPUT_FILE}")
    print("Run with: python dist/robinhood_cli.pyz")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
