#!/usr/bin/env bash
# Book&Ride - Unit 04 : demonstration of every feature through the gateway.
# Usage (from bookandride/) : bash scripts/demo.sh
# All values (port, API keys) come from .env - nothing is hard-coded.

cd "$(dirname "$0")/.." || exit 1
set -a; source .env; set +a                        # export every variable of .env

BASE="http://localhost:${GATEWAY_PORT}"            # the gateway = the only entry point
W='\n\nhttp_code=%{http_code}\n'                   # print the HTTP status after the body
JSON="Content-Type: application/json"
KEY1="X-API-Key: ${API_KEY_USER1}"                 # user 1

echo "### 1. books service health (200)"
curl -s -w "$W" "$BASE/books/health"

echo "### 2. rentals service health (200)"
curl -s -w "$W" "$BASE/rentals/health"

echo "### 3. create a book - public route (201)"
curl -s -w "$W" -X POST "$BASE/books" -H "$JSON" \
     -d '{"title":"Dune","author":"Frank Herbert","stock":5}'

echo "### 4. search books (200)"
curl -s -w "$W" "$BASE/books?search=dune"

echo "### 5. start a rental WITHOUT API key (401)"
curl -s -w "$W" -X POST "$BASE/rentals/start" -H "$JSON" -d '{"bike_id":"BIKE-02"}'

echo "### 6. start a rental WITH the key of user 1 (201)"
BIKE="BIKE-$(date +%H%M%S)"                        # new bike id each run -> no 409 "already rented"
START=$(curl -s -X POST "$BASE/rentals/start" -H "$KEY1" -H "$JSON" -d "{\"bike_id\":\"$BIKE\"}")
echo "$START"
RID=$(echo "$START" | sed -nE 's/.*"rental_id":([0-9]+).*/\1/p')   # id of the rental just created

echo "### 7. stop rental $RID (200, 0.25 EUR)"
curl -s -w "$W" -X POST "$BASE/rentals/stop" -H "$KEY1" -H "$JSON" -d "{\"rental_id\":${RID}}"

echo "### 8. my rentals (200)"
curl -s -w "$W" "$BASE/rentals" -H "$KEY1"

echo "### 9. flood: 40 requests -> some 200, then 429 (limit ${RATE_LIMIT}, burst ${RATE_BURST})"
for i in $(seq 1 40); do curl -s -o /dev/null -w "%{http_code}\n" "$BASE/books"; done | sort | uniq -c
sleep 2                                            # let the rate limit reset

echo "### 10. unknown route, rejected by the gateway (404)"
curl -s -w "$W" "$BASE/unknown"
