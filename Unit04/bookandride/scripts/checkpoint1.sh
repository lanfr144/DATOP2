#!/usr/bin/env bash
# Checkpoint 1 - the gateway is the single entry point
. "$(dirname "$0")/_env.sh"
docker compose up -d --build --wait
docker compose ps
curl -s "$GW/health"; echo                       # the gateway itself
curl -s "$GW/books"; echo                        # forwarded to the books service
curl -s -m 3 "http://localhost:${API_PORT}/health" || echo "port ${API_PORT} not published: OK, the API is hidden behind the gateway"
