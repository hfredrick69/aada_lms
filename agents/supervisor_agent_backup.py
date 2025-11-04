#!/usr/bin/env python3
"""
Supervisor Agent
----------------
Coordinates all other agents (Architect, Developer, QA, DevOps, Docs)
for local builds and testing. Runs Cleanup Agent before each cycle.
"""

import subprocess
import sys
import yaml
import datetime
from pathlib import Path

CONFIG_PATH = Path("agents/config.yaml")
LOG_DIR = Path("/tmp/agent_logs")
LOG_DIR.mkdir(exist_ok=True)


def log(message: str):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = f"[Supervisor] {timestamp} | {message}"
    print(msg)
    with open(LOG_DIR / "supervisor.log", "a") as f:
        f.write(msg + "\n")


def load_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


def run_agent(script: str):
    try:
        log(f"Running {script} ...")
        subprocess.run(["python3", f"agents/{script}"], check=True)
        log(f"✅ Completed {script}")
    except subprocess.CalledProcessError as e:
        log(f"❌ Error running {script}: {e}")


def run_cleanup_agent():
    """Run cleanup_agent.py before each full cycle."""
    log("Running Cleanup Agent before workflow...")
    subprocess.run(["python3", "agents/cleanup_agent.py"], check=False)
    log("Cleanup Agent complete. Continuing workflow...")


def run_task(task_name: str, cfg: dict):
    """Runs a named task from the config file"""
    if task_name not in cfg["tasks"]:
        log(f"Unknown task '{task_name}'")
        return
    agents = cfg["tasks"][task_name]["agents"]
    log(f"Executing task '{task_name}' with agents: {', '.join(agents)}")
    for agent in agents:
        script_name = f"{agent}_agent.py"
        run_agent(script_name)
    log(f"Task '{task_name}' complete.")


def main():
    cfg = load_config()

    # Run Cleanup Agent first for default runs
    if len(sys.argv) == 1:
        run_cleanup_agent()

    # CLI Usage: python3 agents/supervisor_agent.py [task_name]
    if len(sys.argv) > 1:
        task_name = sys.argv[1]
        run_task(task_name, cfg)
    else:
        # Default full-cycle run
        run_order = cfg["agents"]["supervisor"]["run_order"]
        log("Running full agent cycle (default mode)")
        for agent in run_order:
            script_name = f"{agent}_agent.py"
            run_agent(script_name)
        log("All agents complete.")


if __name__ == "__main__":
    main()
