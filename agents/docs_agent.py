#!/usr/bin/env python3
"""
Docs Agent
Generates or updates API documentation from the running FastAPI instance.
"""

import subprocess
import datetime
from pathlib import Path

LOG_DIR = Path("/tmp/agent_logs")
LOG_DIR.mkdir(exist_ok=True)

DOCS_DIR = Path("docs")
DOCS_DIR.mkdir(exist_ok=True)

def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[Docs] {ts} | {msg}")

def main():
    log("Attempting to export OpenAPI schema...")
    subprocess.run(
        ["curl", "-o", "docs/api_schema.json", "http://localhost:8000/openapi.json"],
        check=False
    )

    changelog_path = DOCS_DIR / "CHANGELOG.md"
    with changelog_path.open("a") as f:
        f.write(f"- {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Docs updated locally.\n")

    log("Docs Agent tasks complete.")

if __name__ == "__main__":
    main()
