#!/usr/bin/env python3
"""
DevOps Agent
Detects and manages local Docker containers for AADA LMS/SIS.
"""

import subprocess
import datetime
from pathlib import Path

LOG_DIR = Path("/tmp/agent_logs")
LOG_DIR.mkdir(exist_ok=True)

def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DevOps] {ts} | {msg}")

def container_exists(name: str) -> bool:
    result = subprocess.run(
        ["docker", "ps", "-a", "--format", "{{.Names}}"],
        capture_output=True, text=True
    )
    return name in result.stdout.splitlines()

def main():
    log("Checking running containers...")
    subprocess.run(["docker", "ps"], check=False)

    containers = ["aada_lms-web-1", "aada_admin_portal", "aada_lms-db-1"]
    for name in containers:
        if container_exists(name):
            log(f"✅ Found container '{name}'. No rebuild needed.")
        else:
            log(f"⚠️ Container '{name}' not found. Attempting docker compose up...")
            subprocess.run(["docker", "compose", "up", "-d"], check=False)

    log("Listing all containers for verification:")
    subprocess.run(["docker", "ps", "-a"], check=False)

    log("DevOps tasks complete.")

if __name__ == "__main__":
    main()
