#!/usr/bin/env python3
"""
Frontend Generator Agent
Uses Codex (GPT-5-Codex) to scaffold new UI components from design + OpenAPI schema.
"""

import datetime
import subprocess
from pathlib import Path

LOG = Path("/tmp/agent_logs/frontend_generator.log")


def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[Frontend-Gen] {ts} | {msg}")
    LOG.write_text(f"{ts} | {msg}\n", append=True)


def main():
    log("Starting Codex-based frontend generation...")
    cmd = [
        "codex", "run",
        "--model", "gpt-5-codex",
        "--instructions", "codex_instructions_frontend.md",
        "--output", "frontend/src/pages/"
    ]
    subprocess.run(cmd, check=False)
    log("Codex generation complete — review output in frontend/src/pages/")
