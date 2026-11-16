#!/usr/bin/env bash
# Checkpoint 2 - API keys and rate limiting at the gateway
. "$(dirname "$0")/_env.sh"
echo "# 1) no key -> 401"
curl -s -i -X POST "$GW/rentals/start" -H "Content-Type: application/json" -d '{"bike_id":"BIKE-02"}' | sed -n '1p;$p'; echo
echo "# 2) valid key -> 201, user_id chosen by the gateway"
curl -s -X POST "$GW/rentals/start" -H "X-API-Key: $API_KEY_USER2" -H "Content-Type: application/json" -d '{"bike_id":"BIKE-02"}'; echo
echo "# 3) try to cheat with X-User-Id: 1"
curl -s -X POST "$GW/rentals/start" -H "X-API-Key: $API_KEY_USER2" -H "X-User-Id: 1" -H "Content-Type: application/json" -d '{"bike_id":"BIKE-03"}'; echo
curl -s "$GW/rentals" -H "X-API-Key: $API_KEY_USER2"; echo
echo "# 4) flood: 40 requests (expected about 21-26 x 200, the rest 429)"
for i in $(seq 1 40); do curl -s -o /dev/null -w "%{http_code}\n" "$GW/books"; done | sort | uniq -c
