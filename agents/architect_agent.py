#!/usr/bin/env python3
"""
Architect Agent
Performs static checks and applies Alembic migrations.
"""

import subprocess
import datetime
from pathlib import Path

LOG_DIR = Path("/tmp/agent_logs")
LOG_DIR.mkdir(exist_ok=True)


def log(message: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[Architect] {ts} | {message}")


def main():
    log("Checking Python code style with flake8...")
    subprocess.run(["flake8", "app"], check=False)
    log("Running Alembic migrations...")
    subprocess.run(["alembic", "upgrade", "head"], check=False)
    log("Architect tasks complete.")


if __name__ == "__main__":
    main()
