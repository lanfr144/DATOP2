# Unit 01 – GESTEL API (Python + FastAPI + MySQL)

Petite API REST avec une interface web de connexion/inscription, plus les scripts
des exercices du lab *Unit 01 – API Basics* (HTTP, JSON).

## Arborescence

```
Unit01/
├── .env                  ← configuration réelle (NE PAS committer, dans .gitignore)
├── .env.example          ← modèle : mêmes clés, secrets = PASSWORD_<NOM>
├── docker-compose.yml    ← MySQL 8 + API
├── api/
│   ├── Dockerfile, requirements.txt, pytest.ini, alembic.ini
│   ├── app/
│   │   ├── main.py       ← création de l'app FastAPI (lifespan : tables + admin de démo)
│   │   ├── config.py     ← lecture du .env (ports, BD, secrets)
│   │   ├── database.py   ← engine SQLAlchemy (MySQL, repli SQLite)
│   │   ├── models.py     ← table users
│   │   ├── schemas.py    ← UserCreate / UserRead (Pydantic)
│   │   ├── crud.py       ← accès aux données
│   │   ├── utils.py      ← bcrypt + JWT
│   │   ├── auth.py       ← cookie de session
│   │   ├── routers/      ← users.py (API JSON) · ui.py (pages HTML)
│   │   └── templates/    ← login, register, dashboard, docs
│   ├── migrations/       ← Alembic (révision 0001 : table users)
│   ├── scripts/check_mysql_connection.py
│   └── tests/test_api.py
├── exercises/            ← example1.py (REST Open-Meteo) et example2.py (GraphQL) du cours, ex1_http.py, ex2_json.py
└── docs/                 ← sujet PDF, answers.md (réponses théoriques), adr/
```

## Démarrage rapide

### Option A – tout dans Docker (MySQL inclus)
```bash
cp .env.example .env          # puis remplacer les valeurs PASSWORD_*
docker compose up -d --build
curl http://localhost:8000/healthy
```

### Option B – en local (Windows PowerShell)
```powershell
copy .env.example .env        # puis remplacer les valeurs PASSWORD_*
cd api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m app.main            # host/port lus dans .env (APP_HOST / APP_PORT)
```
Si MySQL n'est pas joignable (`DATABASE_URL`), l'API bascule sur `sqlite:///./gestel.db`
et affiche `Warning: MySQL unreachable`. Pour démarrer seulement MySQL : `docker compose up -d mysql`
(port publié : `MYSQL_HOST_PORT`, 3307 par défaut car 3306 est souvent déjà pris).

Diagnostic : `python scripts/check_mysql_connection.py`

## Ports et variables (.env)

| Variable | Défaut | Rôle |
|---|---|---|
| `APP_HOST` / `APP_PORT` | 127.0.0.1 / 8000 | écoute d'uvicorn (local et conteneur) |
| `APP_HOST_PORT` | 8000 | port publié par docker compose |
| `MYSQL_PORT` | 3306 | port interne du conteneur MySQL |
| `MYSQL_HOST_PORT` | 3307 | port MySQL publié sur 127.0.0.1 |
| `DATABASE_URL` | `mysql+pymysql://${MYSQL_USER}:${MYSQL_PASSWORD}@…` | construit à partir des autres variables |
| `SECRET_KEY` | – | clé de signature des JWT |
| `ADMIN_EMAIL` / `ADMIN_PASSWORD` | admin@example.com | compte admin créé au démarrage |

## Endpoints

| Méthode | URL | Description |
|---|---|---|
| GET | `/healthy` | health check |
| POST | `/users` | créer un utilisateur (201 + `Location`, 409 si email déjà pris, 422 si invalide) |
| GET | `/users` | lister (`skip`, `limit`) |
| GET | `/users/{id}` | lire un utilisateur (404 si inconnu) |
| GET/POST | `/login`, `/register` | pages HTML |
| GET | `/dashboard` | tableau de bord (connexion requise ; l'admin voit la liste des utilisateurs) |
| GET | `/docs` | Swagger UI dans l'interface (connexion requise) — brut sur `/swagger`, `/redoc`, `/openapi.json` |
| GET | `/logout` | déconnexion |

## Tests
```bash
cd api
pytest -q          # 4 tests, base SQLite temporaire : pas besoin de MySQL
```

## Migrations (Alembic)
```bash
cd api
alembic upgrade head                                   # applique les migrations
alembic revision --autogenerate -m "describe change"   # après modification de models.py
```
Remarque : au démarrage, l'application fait aussi `create_all()` (pratique pour le lab).
En production on utiliserait seulement Alembic.

## Exercices du lab
```bash
pip install requests
python exercises/ex1_http.py    # GET / POST / 404 sur JSONPlaceholder
python exercises/ex2_json.py    # json.loads / json.dumps
python exercises/example1.py    # exemple REST du cours (météo Luxembourg)
python exercises/example2.py LU # exemple GraphQL du cours (pays)
```
Réponses écrites : [docs/answers.md](docs/answers.md).

## Corrections apportées (2026-10-28)
- `crud.py` contenait une copie de `main.py` et `schemas.py` une copie de `utils.py` : réécrits.
- Indentation cassée (`IndentationError`) dans `main.py`, `auth.py`, `database.py` : corrigée.
- Imports relatifs (`from . import crud`) impossibles sans package : code déplacé dans `api/app/`.
- Templates introuvables (chemin relatif `templates`) : chemin absolu + nouvelle signature `TemplateResponse(request, ...)`.
- `passlib` (non maintenu) et `python-jose` remplacés par `bcrypt` et `PyJWT` ; `datetime.utcnow()` (déprécié) remplacé.
- `alembic.ini` invalide (pas de section `[alembic]`, pas de dossier migrations) : configuration complète.
- Ports, mots de passe et URL de BD sortis du code vers `.env`.

## Synchronisation avec le cours (2e passe, 2026-10-28)
- Le cours *Unit 01 – API Basics* cite `unit01/example1.py` (REST) et `example2.py` (GraphQL) :
  ils sont maintenant dans `exercises/` (avec timeout et gestion des erreurs GraphQL).
- Codes de statut alignés sur le cheat sheet *Unit 04bis* : email déjà utilisé → **409 Conflict**
  (au lieu de 400), données invalides du formulaire → **422**, création → **201 + `Location: /users/{id}`**.
- Healthcheck : `HEALTHCHECK` dans `api/Dockerfile` (GET `/healthy`) ; MySQL a le sien dans `docker-compose.yml`.
