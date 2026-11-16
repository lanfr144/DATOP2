# Charge le .env du projet (ports) ; utilise par les scripts checkpoint*.sh
cd "$(dirname "$0")/.."
[ -f .env ] || cp .env.example .env
set -a; . ./.env; set +a
API="http://localhost:${API_HOST_PORT}"
