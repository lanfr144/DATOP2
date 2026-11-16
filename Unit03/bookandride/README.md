# Book&Ride – Unit 03 : le monolithe

API FastAPI (modules **books** et **rentals**) + PostgreSQL, lancée avec Docker Compose.

```
bookandride/
├── docker-compose.yml        ← db (PostgreSQL 16) + api
├── .env / .env.example       ← ports, identifiants (.env jamais commité)
├── docs/adr/ADR-001-architecture.md
├── scripts/checkpoint2.sh … checkpoint4.sh   ← les commandes "TERMINAL" du sujet
└── api/
    ├── Dockerfile, requirements.txt, pytest.ini
    ├── app/  main.py · db.py · models.py · schemas.py · pricing.py
    │   └── routers/  books.py (module 1) · rentals.py (module 2)
    └── tests/ test_pricing.py · test_api.py
```

## Démarrage
```bash
cp .env.example .env            # puis remplacer PASSWORD_DB_PASSWORD
docker compose up -d --build --wait
curl http://localhost:8080/health          # {"status":"ok","version":"0.1.0"}
docker compose exec api pytest -q          # 14 passed
```
Swagger UI : http://localhost:8080/docs — Windows PowerShell : utiliser `curl.exe`.

Scripts (bash/WSL) : `bash scripts/checkpoint2.sh`, `checkpoint3.sh`, `checkpoint4.sh`.

| Variable (.env) | Défaut | Rôle |
|---|---|---|
| `API_PORT` | 8080 | port d'uvicorn dans le conteneur |
| `API_HOST_PORT` | 8080 | port publié sur la machine |
| `DB_HOST` / `DB_PORT` | db / 5432 | PostgreSQL dans le réseau Docker (non publié) |
| `DB_USER` / `DB_PASSWORD` / `DB_NAME` | app / … / bookandride | identifiants |

Si vous changez `DB_PASSWORD` après le premier lancement : `docker compose down -v` (efface les données).

## Endpoints
| Méthode | URL | Résultat |
|---|---|---|
| GET | `/health` | 200 ou 503 si la BD est indisponible |
| GET | `/books?search=…&author=…` | liste (recherche titre/auteur ; `author` = stretch goal) |
| POST / GET / PUT / DELETE | `/books`, `/books/{id}` | CRUD (201, 200, 200, 204 ; 404 ; 422) |
| POST | `/rentals/start` `{"bike_id":"BIKE-01"}` | 201, 409 si le vélo est déjà loué |
| POST | `/rentals/stop` `{"rental_id":1}` | prix = 0,25 €/minute entamée, plafonné à 12 € **par jour** |
| GET | `/rentals/{id}` | une location (cible de l'en-tête `Location`) |
| GET | `/rentals`, `/rentals/me` (header `X-User-Id`) | toutes les locations / les miennes (stretch goal) |

## Réponses – Check your understanding
1. **Pourquoi un monolithe aujourd'hui ?** Petite équipe, trafic faible et homogène, données partagées
   (cohérence forte), besoin d'un produit qui marche vite : un seul code, un seul déploiement, un seul log.
2. **Deux signaux pour passer aux microservices :** un module dont la charge diverge fortement
   (rentals ×100) et doit être mis à l'échelle seul ; plusieurs équipes qui veulent livrer à des rythmes différents.
3. **Si PostgreSQL tombe :** les endpoints métier renvoient des erreurs 500, `/health` renvoie
   **503 `database unavailable`** (il exécute `SELECT 1`). `pool_pre_ping` permet de se reconnecter
   automatiquement quand la base revient.
4. **Pourquoi le monolithe modulaire facilite l'Unit 04 :** rentals est déjà isolé (router, modèle,
   schémas, pricing) : l'extraire revient à copier ces fichiers dans un nouveau service, sans démêler du code mélangé.

## Corrections apportées (2026-10-28)
- `books.py` : TODO de `PUT` et `DELETE` implémentés ; `test_pricing.py` : tests manquants écrits.
- Lignes parasites copiées du PDF (`flange  API/APP/MAIN.PY (ADD)`…) supprimées dans `main.py`, `models.py`, `schemas.py` → plus de `SyntaxError`.
- `app/__init__.py` et `routers/__init__.py` ajoutés ; `main.py` inclut les deux routers.
- `dockerfile` renommé `Dockerfile` ; conteneur exécuté en utilisateur non-root.
- `DOCKER-COMPOSE.YML` (indentation perdue) réécrit ; healthchecks : `pg_isready` pour `db`, `HEALTHCHECK` dans `api/Dockerfile` (GET `/health`).
- Ports et mot de passe : plus rien en dur, tout vient de `.env` ; `DATABASE_URL` construite à partir des variables.
- Stretch goals : tous faits — `GET /books?author=`, `GET /rentals/me`, utilisateur non-root, plafond de 12 € **par jour**.

## Plafond journalier (stretch goal)
`app/pricing.py` : chaque journée complète de 24 h coûte 12 €, les minutes restantes 0,25 € chacune,
de nouveau plafonnées à 12 €.

| Durée | Prix |
|---|---|
| 40 min | 10,00 € |
| 100 min | 12,00 € |
| 24 h | 12,00 € |
| 24 h + 1 min | 12,25 € |
| 24 h + 100 min | 24,00 € |
| 2 jours + 2 h | 36,00 € |

Testé dans `tests/test_pricing.py` (9 tests) et de bout en bout dans `tests/test_api.py::test_daily_cap_on_a_long_rental`.

## Synchronisation avec le cheat sheet HTTP (Unit 04bis)
`POST /books` et `POST /rentals/start` renvoient **201 + `Location`** (`/books/{id}`, `/rentals/{id}`).
