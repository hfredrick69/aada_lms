curl https://api.anthropic.com/v1/messages \
--header "x-api-key: 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"
-header "anthropic-version: 2023-06-01" \
--header "content-type: application/json" \
-data l
'{
"model": "claude-sonnet-4-20250514",
"max_tokens": 1024,
"messages": [
{"role": "user", "content": "Hello, world"}
]
}'
