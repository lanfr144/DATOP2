import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from sqlalchemy import text

from . import models  # noqa: F401  (registers the tables in Base.metadata)
from .db import Base, engine
from .routers import books, rentals

APP_VERSION = os.getenv("APP_VERSION", "0.1.0")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)     # create the tables if they don't exist
    yield


app = FastAPI(title="Book&Ride API (monolith)", version=APP_VERSION, lifespan=lifespan)


@app.get("/health", tags=["health"])
def health():
    # /health also checks the database: if PostgreSQL is down, the API answers 503
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        raise HTTPException(status_code=503, detail="database unavailable")
    return {"status": "ok", "version": APP_VERSION}


# one codebase, several modules: this is a (modular) monolith
app.include_router(books.router)
app.include_router(rentals.router)
