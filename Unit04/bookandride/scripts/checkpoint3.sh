#!/usr/bin/env bash
# Checkpoint 3 - rentals extracted into its own service + failure isolation
. "$(dirname "$0")/_env.sh"
sleep 2   # let the rate limiter of checkpoint 2 refill
curl -s "$GW/books/health"; echo
curl -s "$GW/rentals/health"; echo
RID=$(curl -s -X POST "$GW/rentals/start" -H "X-API-Key: $API_KEY_USER1" -H "Content-Type: application/json" \
      -d '{"bike_id":"BIKE-07"}' | tee /dev/stderr | python3 -c "import sys,json; print(json.load(sys.stdin)['rental_id'])"); echo
curl -s -X POST "$GW/rentals/stop" -H "X-API-Key: $API_KEY_USER1" -H "Content-Type: application/json" -d "{\"rental_id\":$RID}"; echo
docker compose exec rentals pytest -q
echo "# failure isolation"
docker compose stop rentals
curl -s -o /dev/null -w "books:   %{http_code}\n" "$GW/books"
curl -s -o /dev/null -w "rentals: %{http_code}\n" "$GW/rentals" -H "X-API-Key: $API_KEY_USER1"
docker compose start rentals
