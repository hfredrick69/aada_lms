#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).parent
AGENTS_DIR = ROOT / "agents"
RUNNER = ROOT / "run_agents.sh"


def main():
    AGENTS_DIR.mkdir(parents=True, exist_ok=True)
    runner_content = "#!/bin/bash\n" \
                     "echo \"Starting AADA Local Agent Workflow...\"\n" \
                     "python3 agents/supervisor_agent.py \"$@\"\n"
    RUNNER.write_text(runner_content)
    RUNNER.chmod(0o755)

    print("✅ Created/verified:")
    print(f" - agents/ -> {AGENTS_DIR.resolve()}")
    print(f" - run_agents.sh -> {RUNNER.resolve()}")


if __name__ == "__main__":
    main()
