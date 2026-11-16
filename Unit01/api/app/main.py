"""
GESTEL API - point d'entree FastAPI.

Lancer en local (depuis le dossier api/) :
    python -m app.main                 # host/port lus dans le .env (APP_HOST / APP_PORT)
ou
    uvicorn app.main:app --reload --host $APP_HOST --port $APP_PORT
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import crud, models, schemas
from .config import ADMIN_EMAIL, ADMIN_NAME, ADMIN_PASSWORD, APP_HOST, APP_PORT
from .database import SessionLocal, engine
from .routers import ui, users


def _ensure_demo_user() -> None:
    """Cree le compte administrateur de demo s'il n'existe pas encore (lab uniquement)."""
    with SessionLocal() as db:
        if not crud.get_user_by_email(db, email=ADMIN_EMAIL):
            crud.create_user(db, schemas.UserCreate(name=ADMIN_NAME, email=ADMIN_EMAIL,
                                                    password=ADMIN_PASSWORD))


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Correction : creation des tables + du compte demo au DEMARRAGE de l'application,
    # et non plus a l'import du module (ce qui rendait les tests et Alembic difficiles).
    models.Base.metadata.create_all(bind=engine)
    _ensure_demo_user()
    yield


app = FastAPI(
    title="GESTEL API",
    description="A simple REST API with login UI.",
    version="0.1.0",
    docs_url="/swagger",       # Swagger UI brut (embarque dans la page /docs)
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS : "*" est pratique en developpement. Attention : avec allow_credentials=True,
# il faut lister des origines precises en production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthy", tags=["health"])
def healthy():
    return {"status": "ok"}


app.include_router(users.router)
app.include_router(ui.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=APP_HOST, port=APP_PORT, reload=True)
