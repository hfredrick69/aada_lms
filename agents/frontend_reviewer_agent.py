#!/usr/bin/env python3
"""
Frontend Reviewer Agent
Uses Claude-Code to review newly generated UI for quality, accessibility, and consistency.
"""

import datetime
import subprocess
from pathlib import Path

LOG = Path("/tmp/agent_logs/frontend_review.txt")


def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[Frontend-Review] {ts} | {msg}")
    LOG.write_text(f"{ts} | {msg}\n", append=True)


def main():
    log("Starting Claude-Code review of frontend...")
    cmd = [
        "claude", "code", "review",
        "frontend/src/",
        "--summary-file", str(LOG)
    ]
    subprocess.run(cmd, check=False)
    log("Claude-Code review complete — see /tmp/agent_logs/frontend_review.txt")
