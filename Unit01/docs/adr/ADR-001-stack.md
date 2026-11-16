# ADR-001 : choix techniques de l'API GESTEL

## Statut
Accepté – 2026-10-28

## Contexte
Petite API de démonstration (utilisateurs + login) réalisée pendant l'Unit 01, par une seule personne,
à lancer sur un poste Windows/WSL avec ou sans MySQL.

## Décision
- **FastAPI** : validation automatique (Pydantic) et documentation OpenAPI générée (`/swagger`, `/redoc`).
- **SQLAlchemy 2 + MySQL 8**, avec **repli automatique sur SQLite** si MySQL est injoignable.
- **Alembic** pour versionner le schéma (`api/migrations`).
- **bcrypt** pour les mots de passe et **JWT dans un cookie HTTP-only** pour la session web.
- Toute la configuration (ports, mots de passe, URL de BD) est dans **`.env`** (jamais commité),
  avec un modèle **`.env.example`** où les secrets valent `PASSWORD_<NOM>`.

## Conséquences
+ Lancement simple (`python -m app.main`) ou complet (`docker compose up`).
+ Tests rapides sur SQLite, sans serveur MySQL.
- Le repli SQLite peut masquer une mauvaise config MySQL : surveiller le message `Warning: MySQL unreachable`.
- Les endpoints `/users` ne sont pas protégés : à sécuriser avant toute mise en production.
