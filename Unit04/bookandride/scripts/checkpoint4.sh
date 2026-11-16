#!/usr/bin/env bash
# Checkpoint 4 - metrics (internal: read from inside the container)
. "$(dirname "$0")/_env.sh"
docker compose up -d --wait rentals          # wait until rentals is healthy (e.g. after checkpoint 3)
# counters live in memory and restart at 0 with the container: generate some activity first
RID=$(curl -s -X POST "$GW/rentals/start" -H "X-API-Key: $API_KEY_USER1" -H "Content-Type: application/json" \
      -d '{"bike_id":"BIKE-09"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['rental_id'])")
curl -s -o /dev/null -X POST "$GW/rentals/stop" -H "X-API-Key: $API_KEY_USER1" -H "Content-Type: application/json" -d "{\"rental_id\":$RID}"
docker compose exec rentals python -c \
  "import os, urllib.request; print(urllib.request.urlopen(f'http://localhost:{os.environ[\"API_PORT\"]}/metrics').read().decode())" \
  | grep -E "^rentals_|^http_requests_total"
echo "Optional Prometheus: docker compose --profile monitoring up -d  ->  http://localhost:${PROMETHEUS_PORT}"
