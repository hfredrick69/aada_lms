#!/usr/bin/env python3
"""
Developer Agent
Runs backend unit tests and optionally builds the frontend.
"""

import subprocess
import datetime
from pathlib import Path

LOG_DIR = Path("/tmp/agent_logs")
LOG_DIR.mkdir(exist_ok=True)

def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[Developer] {ts} | {msg}")

def main():
    log("Running Python unit tests...")
    subprocess.run(["pytest", "-q"], check=False)

    log("Attempting to build React admin portal (if dependencies installed)...")
    subprocess.run(["npm", "run", "build"], cwd="admin_portal", check=False)

    log("Developer tasks complete.")

if __name__ == "__main__":
    main()
