#!/usr/bin/env python3
"""
Build a standalone executable using PyInstaller.

Usage:
  python scripts/build_executable.py
"""

from pathlib import Path
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DIST_DIR = PROJECT_ROOT / "dist"


def main() -> int:
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name",
        "RobinhoodTradingCLI",
        "--onefile",
        "--console",
        str(PROJECT_ROOT / "main.py"),
    ]
    result = subprocess.run(command, cwd=PROJECT_ROOT, check=False)
    if result.returncode != 0:
        print("PyInstaller build failed. Ensure PyInstaller is installed.", file=sys.stderr)
        return result.returncode

    output_path = DIST_DIR / "RobinhoodTradingCLI"
    print(f"Created: {output_path}")
    print("Run with: ./dist/RobinhoodTradingCLI")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
