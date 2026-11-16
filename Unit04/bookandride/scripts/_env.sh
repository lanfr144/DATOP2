# Charge le .env du projet ; utilise par les scripts checkpoint*.sh
cd "$(dirname "$0")/.."
[ -f .env ] || cp .env.example .env
set -a; . ./.env; set +a
GW="http://localhost:${GATEWAY_PORT}"
