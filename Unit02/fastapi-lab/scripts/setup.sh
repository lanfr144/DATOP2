#!/usr/bin/env bash
# Unit 02a - installation et lancement (Linux / macOS / WSL).
# Correction de l'ancien "new 1" : il RECREAIT main.py (ecrasant le code) et finissait par "&& Li".
# A lancer depuis le dossier fastapi-lab/ :  bash scripts/setup.sh
set -euo pipefail

[ -f .env ] || cp .env.example .env
set -a; . ./.env; set +a                # charge APP_HOST / APP_PORT

python3 -m venv venv
. venv/bin/activate
pip install -r api/requirements.txt
pip list | grep -Ei 'fastapi|uvicorn'

cd api
pytest -q
echo "API -> http://${APP_HOST}:${APP_PORT}/docs"
uvicorn app.main:app --reload --host "${APP_HOST}" --port "${APP_PORT}"
