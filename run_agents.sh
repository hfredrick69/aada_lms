#!/bin/bash
echo "Starting AADA Local Agent Workflow..."
python3 agents/supervisor_agent.py "$@"
