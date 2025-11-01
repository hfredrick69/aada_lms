#!/usr/bin/env python3
"""
Cleanup Agent
-------------
Performs safe, smart cleanup for the AADA automation environment.

Actions:
1. Deletes all .pyc files and __pycache__ directories.
2. Removes /tmp/agent_logs files older than 7 days.
3. Preserves recent logs and QA results for debugging.
"""

import os
import datetime
from pathlib import Path
import shutil

LOG_DIR = Path("/tmp/agent_logs")
PROJECT_ROOT = Path(__file__).resolve().parents[1]  # one level up from /agents
RETENTION_DAYS = 7

def log(message: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[Cleanup] {ts} | {message}")

def cleanup_pyc_files():
    log("Starting .pyc and __pycache__ cleanup...")
    deleted_files = 0
    for path in PROJECT_ROOT.rglob("*.pyc"):
        try:
            path.unlink()
            deleted_files += 1
        except Exception as e:
            log(f"⚠️ Could not delete {path}: {e}")

    deleted_dirs = 0
    for path in PROJECT_ROOT.rglob("__pycache__"):
        try:
            shutil.rmtree(path)
            deleted_dirs += 1
        except Exception as e:
            log(f"⚠️ Could not delete {path}: {e}")

    log(f"✅ Removed {deleted_files} .pyc files and {deleted_dirs} __pycache__ directories.")

def cleanup_old_logs():
    if not LOG_DIR.exists():
        log("No /tmp/agent_logs directory found — nothing to clean.")
        return

    log(f"Cleaning logs older than {RETENTION_DAYS} days...")
    now = datetime.datetime.now()
    cutoff = now - datetime.timedelta(days=RETENTION_DAYS)

    for file in LOG_DIR.iterdir():
        if not file.is_file():
            continue
        mtime = datetime.datetime.fromtimestamp(file.stat().st_mtime)
        if mtime < cutoff:
            try:
                file.unlink()
                log(f"🗑️ Deleted old log: {file.name}")
            except Exception as e:
                log(f"⚠️ Could not delete {file.name}: {e}")
        else:
            age_days = (now - mtime).days
            log(f"🕒 Keeping recent log: {file.name} ({age_days} days old)")

def main():
    log("===== AADA Cleanup Agent Starting =====")
    cleanup_pyc_files()
    cleanup_old_logs()
    log("===== Cleanup Agent Complete =====")

if __name__ == "__main__":
    main()
