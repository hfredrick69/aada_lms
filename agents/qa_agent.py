#!/usr/bin/env python3
"""
QA Agent
---------
Runs backend and frontend test suites.
Automatically terminates lingering pytest processes, ensures Vitest exits cleanly,
and saves logs to /tmp/agent_logs/qa_results.txt.
"""

import subprocess
import datetime
from pathlib import Path

LOG_DIR = Path("/tmp/agent_logs")
LOG_DIR.mkdir(exist_ok=True)
RESULT_FILE = LOG_DIR / "qa_results.txt"


def log(msg: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[QA] {ts} | {msg}"
    print(entry)
    with open(RESULT_FILE, "a") as f:
        f.write(entry + "\n")


def kill_pytest():
    """Terminate hanging pytest sessions inside Docker and locally."""
    log("Killing any existing pytest processes...")

    # Kill locally
    subprocess.run(["pkill", "-f", "pytest"], check=False)

    # Check if pkill exists in container
    check_cmd = ["docker", "exec", "aada_lms-web-1", "sh", "-c", "command -v pkill"]
    result = subprocess.run(check_cmd, capture_output=True, text=True)
    if result.returncode == 0:
        subprocess.run(["docker", "exec", "aada_lms-web-1", "pkill", "-f", "pytest"], check=False)
    else:
        log("⚠️  'pkill' not found in container; skipping container cleanup.")


def run_backend_tests():
    """Run backend pytest inside Docker container and capture output."""
    log("Running backend tests (pytest)...")
    with open(RESULT_FILE, "a") as f:
        f.write("\n=== BACKEND TESTS ===\n")
        subprocess.run([
            "docker", "exec", "aada_lms-web-1",
            "pytest", "-vv", "--maxfail=1", "--disable-warnings"
        ], stdout=f, stderr=subprocess.STDOUT, check=False)
    log("Backend tests finished.")


def run_frontend_tests():
    """Run Vitest once (no watch mode) and capture output."""
    log("Running frontend tests (npm test)...")
    with open(RESULT_FILE, "a") as f:
        f.write("\n=== FRONTEND TESTS ===\n")
        subprocess.run(
            ["npm", "run", "test", "--", "--run"],
            cwd="admin_portal",
            stdout=f,
            stderr=subprocess.STDOUT,
            check=False
        )
    log("Frontend tests finished.")


def main():
    # Clear previous log
    RESULT_FILE.write_text(f"QA run started at {datetime.datetime.now()}\n")

    kill_pytest()
    run_backend_tests()
    run_frontend_tests()
    log("QA Agent tasks complete.")


if __name__ == "__main__":
    main()
