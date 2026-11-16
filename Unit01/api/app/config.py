"""
Configuration centralisee de l'application.

Toutes les valeurs (ports, mots de passe, URL de base de donnees...) viennent du
fichier .env (charge par python-dotenv) ou des variables d'environnement.
Aucune valeur sensible ni aucun port n'est code en dur dans le code Python :
les valeurs par defaut ci-dessous ne servent que si la variable est absente.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

# Racine du projet Unit01 (le .env est a cote de docker-compose.yml)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
# override=False : une variable deja definie (ex. par docker compose ou pytest) garde la priorite
load_dotenv(PROJECT_ROOT / ".env", override=False)

# ---------- serveur HTTP (uvicorn) ----------
APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
APP_PORT = int(os.getenv("APP_PORT", "8000"))

# ---------- base de donnees ----------
# Exemple : mysql+pymysql://user:pwd@127.0.0.1:3307/gestel
# python-dotenv remplace ${VAR} par la valeur des autres variables du .env.
SQLITE_FALLBACK_URL = os.getenv("SQLITE_FALLBACK_URL", "sqlite:///./gestel.db")
DATABASE_URL = os.getenv("DATABASE_URL") or SQLITE_FALLBACK_URL

# ---------- securite (JWT stocke dans un cookie) ----------
SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# ---------- compte administrateur de demo (cree au demarrage) ----------
ADMIN_NAME = os.getenv("ADMIN_NAME", "Admin")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "changeme")
