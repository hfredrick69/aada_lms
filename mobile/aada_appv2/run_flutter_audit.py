#!/usr/bin/env python3
"""
Run the AADA Flutter audit via Claude API
Reads your claude_instructions_flutter_audit.md file,
sends it to Claude 3.5 Sonnet, and writes the full report
to AADA_flutter_audit.md.
"""

import os
from anthropic import Anthropic

# 1. Initialize the Anthropic client
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# 2. Read your audit instruction file
with open("claude_instructions_flutter_audit.md") as f:
    prompt = f.read()

# 3. Create Claude message
print("🚀 Running audit with Claude 4 Sonnet ... this may take a few minutes.")
resp = client.messages.create(
model="claude-sonnet-4-20250514",
    max_tokens=6000,
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
)

# 4. Write the output to a Markdown file
output_file = "AADA_flutter_audit.md"
with open(output_file, "w") as out:
    out.write(resp.content[0].text)

print(f"✅ Audit complete! Full report saved to {output_file}")
