# Unit 02 – Frameworks (FastAPI & Django)

| Dossier | Lab | Contenu |
|---|---|---|
| `fastapi-lab/` | 02a – Installing and Running FastAPI | `api/app/main.py` (version du cours), `api/app/lab2a.py` (challenges 1-5 + réponses) |
| `fastapi-post/` | 02b – POST, Validation & Testing | `api/app/main.py` (CRUD en mémoire, Pydantic, pagination, tâche de fond), tests async |
| `django-lab/` | 02c – Django REST Framework | projet `myproject` + app `core` (hello, books CRUD, recherche) |
| `docs/` | | sujets PDF (+ versions OCR) |

Chaque projet a son `.env` (non commité) et son `.env.example` (secrets = `PASSWORD_<NOM>`).
Le port d'écoute est dans `.env` (`APP_PORT` pour FastAPI, `DJANGO_PORT` pour Django).

## 02a – fastapi-lab
```bash
cd fastapi-lab
cp .env.example .env
python -m venv venv && source venv/bin/activate     # Windows : venv\Scripts\activate
pip install -r api/requirements.txt
cd api
pytest -q                     # 5 tests
python -m app.main            # version du cours
python -m app.lab2a           # version avec les challenges (/add, /square, /hello?lang=)
```
Scripts tout-en-un : `bash scripts/setup.sh` (Linux/WSL) ou `scripts\set-up.bat` (Windows).

## 02b – fastapi-post
```bash
cd fastapi-post
cp .env.example .env
pip install -r api/requirements.txt
cd api
pytest -q                     # 13 tests (les 6 du sujet + « Your turn » + test synchrone)
python -m app.main
```

## 02c – django-lab
```bash
cd django-lab
cp .env.example .env          # puis remplacer PASSWORD_DJANGO_SECRET_KEY
pip install -r requirements.txt
python manage.py migrate
python manage.py test         # 4 tests
python manage.py runserver    # host:port lus dans .env (DJANGO_HOST / DJANGO_PORT)
```
Endpoints : `/hello/`, `/hello/<name>/`, `/time/`, `/books/` (GET paginé, POST, `?search=`, `?ordering=`, `?page=`),
`/books/<id>/` (GET, PUT, PATCH, DELETE), `/v1/books/…` (vues « à la main » de l'exercice 3), `/admin/`.

Réponses aux questions et « Your turn » des 3 labs : [docs/answers.md](docs/answers.md).

## Synchronisation avec les sujets (2e passe, 2026-10-28)
- 02a : tests ajoutés pour `/hello/` (404), `/hello/Ada%20Lovelace`, `/items/5`, `price: "cheap"` (exemples du cours Unit 02).
- 02b : tests des « Your turn » (rating 6, sizes ×6, price "cheap", limit=0), exemple curl « Running Shoes », test synchrone `test_root` ; réflexion 404 vs 422.
- 02c : `validate_published` (pas de date future), `get_object_or_404`, `OrderingFilter`, pagination `PAGE_SIZE = 2` ; vues de l'exercice 3 conservées sous `/v1/`.

## Corrections apportées (2026-10-28)
- Fichiers à plat réorganisés en 3 projets (`api/app`, `api/tests`, `docs`).
- **Django** : `urls.py` (projet et app) manquants, vue `hello_world` manquante, app nommée
  `myproject` au lieu de `core`, `IndentationError` dans `views.py` et `settings.py`,
  `SECRET_KEY` codée en dur → `.env`. Migration `0001_initial` et tests ajoutés.
- **02a** : `lab2a.py` lançait `"lab1:app"` (module inexistant) ; port codé en dur → `.env` ;
  `requirements.txt` réduit à l'essentiel (c'était un `pip freeze` de `fastapi[all]`) ;
  le script « new 1 » écrasait `main.py` → remplacé par `scripts/setup.sh` ;
  `set-up.bat` : les `curl` ne s'exécutaient jamais (uvicorn bloquant) et `%{http_code}` doit être doublé dans un `.bat`.
- **02b** : id calculé avec `len(DB)+1` → doublon possible après un DELETE (corrigé + test) ;
  import `from main import ...` → `from app.main import ...`.
- Les dossiers `venv/` existants ont été laissés en place (dans `.gitignore`). Ils ont été créés
  avec Python 3.12 sous WSL ; s'ils ne marchent plus, supprimez-les et recréez-les.
