import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from sqlalchemy import text

from . import models  # noqa: F401  (registers the tables in Base.metadata)
from .db import Base, engine
from .routers import books

APP_VERSION = os.getenv("APP_VERSION", "0.1.0")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)     # create the tables if they don't exist
    yield


# Unit 04: the former monolith now only serves books (rentals moved to rentals-service)
app = FastAPI(title="Book&Ride - books service", version=APP_VERSION, lifespan=lifespan)


@app.get("/health", tags=["health"])
def health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        raise HTTPException(status_code=503, detail="database unavailable")
    return {"status": "ok", "version": APP_VERSION}


app.include_router(books.router)
