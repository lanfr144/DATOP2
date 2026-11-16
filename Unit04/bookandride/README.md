# Book&Ride – Unit 04 : API gateway & microservices

```
client ──:GATEWAY_PORT (8000)──► gateway (NGINX)
                                   ├─ /books…    ──► api (books)         ──► db (PostgreSQL)
                                   └─ /rentals…  ──► rentals (+ X-User-Id) ──► rentals-db (PostgreSQL)
                                       ▲ X-API-Key vérifiée, 10 req/s par IP
prometheus (optionnel) ──scrape /metrics──► rentals
```

```
bookandride/
├── docker-compose.yml          ← 5 conteneurs (+ prometheus avec --profile monitoring)
├── .env / .env.example         ← ports, mots de passe, clés API, limites (.env jamais commité)
├── gateway/templates/default.conf.template   ← config NGINX (variables remplies depuis .env)
├── gateway/nginx.conf.reference              ← version du sujet avec valeurs fixes (non utilisée)
├── prometheus/prometheus.yml.template
├── api/                        ← service books (ex-monolithe) : app/, tests/
├── rentals-service/            ← microservice rentals : app/, tests/ (+ /metrics)
├── docs/adr/ADR-001-architecture.md, ADR-002-api-gateway.md
└── scripts/checkpoint1.sh … checkpoint4.sh
```

## Démarrage (5 étapes)
```bash
cp .env.example .env                      # 1. remplacer les valeurs PASSWORD_*
docker compose up -d --build --wait       # 2. 5 conteneurs "healthy"
curl http://localhost:8000/health         # 3. {"status":"ok","component":"gateway"}
docker compose exec rentals pytest -q     # 4. 12 passed
docker compose exec api pytest -q         # 5. 2 passed
```
Ou les scripts : `bash scripts/checkpoint1.sh` … `checkpoint4.sh`.

> Unit03 et Unit04 utilisent le même nom de projet Compose (`bookandride`) et donc le même volume
> `dbdata` : c'est voulu (les livres créés en Unit03 sont retrouvés), mais ne lancez pas les deux en même temps.

## Démonstration (curl)
```bash
curl  -w '\n\nhttp_code=%{http_code}\n' -s http://localhost:8000/books/health                                   # books service
curl  -w '\n\nhttp_code=%{http_code}\n' -s http://localhost:8000/rentals/health                                 # rentals service
curl  -w '\n\nhttp_code=%{http_code}\n' -s -X POST http://localhost:8000/books -H "Content-Type: application/json" \
     -d '{"title":"Dune","author":"Frank Herbert","stock":5}'                # public : 201
curl  -w '\n\nhttp_code=%{http_code}\n' -s "http://localhost:8000/books?search=dune"
curl  -w '\n\nhttp_code=%{http_code}\n' -i -X POST http://localhost:8000/rentals/start -H "Content-Type: application/json" \
     -d '{"bike_id":"BIKE-02"}'                                              # sans clé : 401
curl  -w '\n\nhttp_code=%{http_code}\n' -s -X POST http://localhost:8000/rentals/start -H "X-API-Key: <API_KEY_USER1>" \
     -H "Content-Type: application/json" -d '{"bike_id":"BIKE-07"}'          # 201, user_id 1
curl  -w '\n\nhttp_code=%{http_code}\n' -s -X POST http://localhost:8000/rentals/stop -H "X-API-Key: <API_KEY_USER1>" \
     -H "Content-Type: application/json" -d '{"rental_id":1}'                # 0.25 €
curl  -w '\n\nhttp_code=%{http_code}\n' -s http://localhost:8000/rentals -H "X-API-Key: <API_KEY_USER1>"        # mes locations
for i in $(seq 1 40); do curl -s -o /dev/null  -w '\n\nhttp_code=%{http_code}\n' http://localhost:8000/books; done | sort | uniq -c   # 429
curl -s http://localhost:8000/unknown                                        # 404 au niveau du gateway
```
Résultats obtenus lors du test (2026-10-28) : 401 sans clé ; un faux `X-User-Id: 1` est écrasé par
le gateway (user_id 2) ; flood = 23 × 200 / 17 × 429 ; `docker compose stop rentals` → books 200, rentals 502.

## Variables (.env)
| Variable | Défaut | Rôle |
|---|---|---|
| `GATEWAY_PORT` | 8000 | seul port publié sur la machine |
| `GATEWAY_LISTEN_PORT` | 80 | port d'écoute de NGINX dans le conteneur |
| `RATE_LIMIT` / `RATE_BURST` | 10r/s / 20 | limitation de débit par IP |
| `API_KEY_USER1` / `API_KEY_USER2` | (secrets) | clés API → user 1 / user 2 |
| `API_PORT`, `RENTALS_PORT` | 8080 | ports internes des services |
| `DB_*`, `RENTALS_DB_*` | | identifiants et ports des 2 PostgreSQL |
| `PROMETHEUS_PORT` | 9090 | Prometheus (127.0.0.1 seulement) |

## Réponses – Check your understanding
1. **Responsabilités prises par le gateway :** authentification (clé API → user id), rate limiting,
   routage par chemin ; aussi masquer les ports internes, rejeter les routes inconnues, journaliser.
2. **Pourquoi rentals ne doit pas publier 8080 :** sinon un client contourne le gateway et envoie
   le `X-User-Id` de son choix ; la sécurité repose sur le gateway comme point d'entrée unique.
3. **Gateway = point de défaillance unique :** plusieurs réplicas derrière un load balancer,
   health checks + redémarrage automatique (`restart: always`, Kubernetes), configuration simple.
4. **Titre du livre avec chaque location :** appel HTTP de rentals vers l'API books (synchrone :
   latence + dépendance) ou copie des données nécessaires via des événements (asynchrone, cohérence
   à terme). Plus de jointure SQL possible.
5. **Le découpage valait-il la peine ?** « Ça dépend » : pour une petite boutique, probablement non
   (complexité > bénéfices) ; oui si rentals doit évoluer/scaler indépendamment ou être confié à une autre équipe.

## Corrections apportées (2026-10-28)
- `docker-compose.yml` (indentation perdue, YAML invalide) réécrit selon la référence du sujet.
- `prometheus.yml` contenait une copie de `test_rentals_api.py` : remplacé par une vraie config.
- `models.py` : `IndentationError` (1re ligne indentée) corrigée.
- Fichiers à plat répartis entre `api/` (books) et `rentals-service/` ; `rentals` retiré du service books.
- `test_api.py` du service books ne testait que books : ajout d'un test « /rentals n'existe plus ici ».
- Ports, mots de passe, clés API et limites de débit : plus aucune valeur en dur, tout vient de `.env`
  (NGINX via template `envsubst`, Prometheus via `sed` au démarrage).
- Healthchecks sur les 6 conteneurs (voir tableau) : le gateway ne démarre que lorsque les services répondent.

## Healthchecks
| Conteneur | Où | Test |
|---|---|---|
| gateway | `docker-compose.yml` | `wget http://127.0.0.1:${GATEWAY_LISTEN_PORT}/health` |
| api | `api/Dockerfile` (`HEALTHCHECK`) | GET `/health` (teste aussi PostgreSQL) |
| rentals | `rentals-service/Dockerfile` (`HEALTHCHECK`) | GET `/rentals/health` (teste aussi sa BD) |
| db, rentals-db | `docker-compose.yml` | `pg_isready` |
| prometheus | `docker-compose.yml` | `wget http://127.0.0.1:${PROMETHEUS_PORT}/-/healthy` |

`docker compose ps` doit afficher `(healthy)` partout ; `docker compose up --wait` attend cet état.

## Synchronisation avec Unit 03 et le cheat sheet HTTP (Unit 04bis)
- `rentals-service` applique la même règle de prix que l'Unit 03 (plafond de 12 € **par jour**).
- **201 + `Location`** sur `POST /books` et `POST /rentals/start` ; `GET /rentals/{id}` (seulement vos locations, sinon 404).
- Erreurs produites par le gateway en **JSON** : `429` avec **`Retry-After: 1`**, `502` / `504`
  (`{"detail": "Upstream service unavailable"}`) au lieu de la page HTML de NGINX.
