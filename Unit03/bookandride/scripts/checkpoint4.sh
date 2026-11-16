#!/usr/bin/env bash
# Checkpoint 4 - tests unitaires + rentals module   (anciens "terminal3" et "terminal4")
. "$(dirname "$0")/_env.sh"
docker compose exec api pytest -q
curl -s -X POST "$API/rentals/start" -H "Content-Type: application/json" -d '{"bike_id": "BIKE-01"}'; echo
curl -s -X POST "$API/rentals/start" -H "Content-Type: application/json" -d '{"bike_id": "BIKE-01"}'; echo   # 409
curl -s -X POST "$API/rentals/stop" -H "Content-Type: application/json" -d '{"rental_id": 1}'; echo
curl -s "$API/rentals"; echo
docker compose exec db psql -U "$DB_USER" -d "$DB_NAME" -c '\dt'
