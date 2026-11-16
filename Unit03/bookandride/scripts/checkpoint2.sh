#!/usr/bin/env bash
# Checkpoint 2 - setup : PostgreSQL + API, /health   (ancien "terminal1")
. "$(dirname "$0")/_env.sh"
docker compose up -d --build --wait
docker compose ps                  # both services "running", db "healthy"
curl -s "$API/health"; echo        # {"status":"ok","version":"0.1.0"}
