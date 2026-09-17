#!/usr/bin/env bash
# Run the Yomeru ML Sidecar server
cd "$(dirname "$0")"
exec .venv/bin/uvicorn server:app --host 127.0.0.1 --port 8000 "$@"
