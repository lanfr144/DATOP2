"""
Connexion a la base de donnees (SQLAlchemy 2.x).

- On utilise MySQL si DATABASE_URL pointe vers MySQL et que le serveur repond.
- Sinon on retombe sur un fichier SQLite local (pratique pour developper sans MySQL).
"""
from pathlib import Path

from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import make_url
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import DATABASE_URL as CONFIGURED_URL, SQLITE_FALLBACK_URL


def _make_engine(url: str):
    # check_same_thread=False : SQLite refuse sinon d'etre utilise depuis plusieurs threads
    # (FastAPI execute les endpoints "def" dans un pool de threads).
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    # pool_pre_ping : verifie la connexion avant usage (MySQL ferme les connexions inactives)
    return create_engine(url, pool_pre_ping=True, connect_args=connect_args)


DATABASE_URL = CONFIGURED_URL
engine = _make_engine(DATABASE_URL)

# Tester la connexion une fois au demarrage : si MySQL est injoignable, fallback SQLite.
try:
    with engine.connect():
        pass
except Exception as exc:  # noqa: BLE001 - on veut attraper toute erreur de connexion
    if DATABASE_URL.startswith("mysql"):
        print(f"Warning: MySQL unreachable ({exc.__class__.__name__}); falling back to {SQLITE_FALLBACK_URL}")
        DATABASE_URL = SQLITE_FALLBACK_URL
        engine = _make_engine(DATABASE_URL)
    else:
        raise

# Avec SQLite, un ancien fichier peut avoir un schema perime (colonne hashed_password absente).
# Dans ce cas on supprime le fichier : create_all() recreera les tables au demarrage.
if DATABASE_URL.startswith("sqlite"):
    try:
        inspector = inspect(engine)
        if "users" in inspector.get_table_names():
            cols = [c["name"] for c in inspector.get_columns("users")]
            if "hashed_password" not in cols:
                sqlite_path = Path(make_url(DATABASE_URL).database)
                if sqlite_path.exists():
                    print("Warning: SQLite schema is out of date; recreating", sqlite_path)
                    engine.dispose()
                    sqlite_path.unlink()
                    engine = _make_engine(DATABASE_URL)
    except Exception:  # noqa: BLE001
        # Si l'inspection echoue, on laisse SQLAlchemy creer le schema normalement.
        pass

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependance FastAPI : une session SQLAlchemy par requete, toujours refermee."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
