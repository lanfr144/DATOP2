# DATOP2 – Exercices

| Unit | Cours (`../COURS/UnitXX`) | Projet(s) | Lancer les tests |
|---|---|---|---|
| 01 | API Basics | `Unit01/` GESTEL API (FastAPI + MySQL, login) + `exercises/` (HTTP, JSON) | `cd Unit01/api && pytest -q` |
| 02 | Frameworks | `Unit02/fastapi-lab` (02a), `Unit02/fastapi-post` (02b), `Unit02/django-lab` (02c) | `pytest -q` / `python manage.py test` |
| 03 | Monolith vs Microservices | `Unit03/bookandride` (monolithe FastAPI + PostgreSQL) | `docker compose exec api pytest -q` |
| 04 | API Gateway | `Unit04/bookandride` (NGINX + books + rentals + Prometheus) | `docker compose exec rentals pytest -q` |

Structure commune des projets : `api/app` (code), `api/app/routers` (modules), `api/tests`, `docs/adr`.

Configuration : chaque projet a un `.env` (réel, **ignoré par git**) et un `.env.example`
(même contenu, mots de passe remplacés par `PASSWORD_<NOM_DE_LA_VARIABLE>`). Les ports ne sont plus
codés en dur : ils sont tous dans les `.env`.

Une sauvegarde de l'état avant la réorganisation (2026-10-28) est dans `../_backup/`.

## Synchronisation COURS ↔ EXERCISES (vérifiée le 2026-10-28)

| Unit | Support de cours | Ce qui a été aligné dans les exercices |
|---|---|---|
| 01 | *API Basics (COURSE)* cite `unit01/example1.py` (REST) et `example2.py` (GraphQL) | copiés et commentés dans `Unit01/exercises/` ; réponses au lab dans `Unit01/docs/answers.md` |
| 02 | *Frameworks (COURSE)* + labs 02a/02b/02c (PDF identiques dans `COURS` et `Unit02/docs`) | tous les « Your turn » / challenges implémentés et testés ; réponses dans `Unit02/docs/answers.md` |
| 03 | *Monolith vs Microservices* (PDF/PPTX identiques) | code conforme à la solution + 4 stretch goals, dont le plafond de 12 €/jour |
| 04 | *API Gateway* (version élève dans `COURS`, solution dans `Unit04/docs`) | code conforme à la solution de référence ; même règle de prix que l'Unit 03 |
| 04bis | *HTTP Status Codes & Methods – Cheat Sheet* | 201 + `Location` sur les créations, 409 pour un conflit (Unit01), 429 + `Retry-After`, 502/504 en JSON au gateway |

Healthchecks Docker : chaque conteneur (API, bases, gateway, Prometheus) en a un ;
`docker compose ps` affiche `(healthy)` et `docker compose up --wait` attend cet état.
