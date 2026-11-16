"""
Book&Ride - rentals microservice (Unit 04).

Routes are prefixed with /rentals so the gateway can forward /rentals/... unchanged.
X-User-Id is mandatory: it is set by the gateway after checking the X-API-Key.
This service must NOT publish its port: otherwise clients could bypass the gateway
and send any X-User-Id.
"""
import math
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response, status
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from .db import Base, engine, get_db
from .models import Rental
from .pricing import calculate_price
from .schemas import RentalStart, RentalStop

APP_VERSION = os.getenv("APP_VERSION", "0.2.0")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Book&Ride - rentals service", version=APP_VERSION, lifespan=lifespan)

# ---------- metrics (Checkpoint 4) ----------
REQUESTS = Counter("http_requests_total", "HTTP requests", ["method", "path", "status"])
LATENCY = Histogram("http_request_duration_seconds", "Request latency", ["path"])
RENTALS_STARTED = Counter("rentals_started_total", "Rentals started")
REVENUE = Counter("rentals_revenue_eur_total", "Revenue in euros")


# counts every request and measures its duration (exported on /metrics)
@app.middleware("http")
async def count_requests(request: Request, call_next):
    path = request.url.path
    with LATENCY.labels(path).time():
        response = await call_next(request)
    REQUESTS.labels(request.method, path, str(response.status_code)).inc()
    return response


# /metrics is internal: the gateway does not route it, Prometheus scrapes it directly
@app.get("/metrics", include_in_schema=False)
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# ---------- health ----------
@app.get("/rentals/health", tags=["health"])
def health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        raise HTTPException(status_code=503, detail="database unavailable")
    return {"status": "ok", "service": "rentals", "version": APP_VERSION}


# ---------- business endpoints (moved from the monolith) ----------
@app.post("/rentals/start", status_code=status.HTTP_201_CREATED, tags=["rentals"])
def start_rental(payload: RentalStart, response: Response, db: Session = Depends(get_db),
                 x_user_id: int = Header()):        # set by the gateway: no default anymore
    busy = db.scalar(select(Rental).where(Rental.bike_id == payload.bike_id,
                                          Rental.stopped_at.is_(None)))
    if busy:
        raise HTTPException(status_code=409, detail=f"{payload.bike_id} is already rented")
    rental = Rental(user_id=x_user_id, bike_id=payload.bike_id,
                    started_at=datetime.now(timezone.utc))
    db.add(rental)
    db.commit()
    db.refresh(rental)
    RENTALS_STARTED.inc()
    response.headers["Location"] = f"/rentals/{rental.id}"   # 201 + Location (cheat sheet 04bis)
    return {"rental_id": rental.id, "bike_id": rental.bike_id, "user_id": rental.user_id,
            "started_at": rental.started_at.isoformat()}


@app.post("/rentals/stop", tags=["rentals"])
def stop_rental(payload: RentalStop, db: Session = Depends(get_db),
                x_user_id: int = Header()):
    rental = db.get(Rental, payload.rental_id)
    if rental is None or rental.user_id != x_user_id:   # you can only stop your own rental
        raise HTTPException(status_code=404, detail="Rental not found")
    if rental.stopped_at is not None:
        raise HTTPException(status_code=409, detail="Rental already stopped")
    now = datetime.now(timezone.utc)
    started = rental.started_at
    if started.tzinfo is None:                 # SQLite drops the timezone
        started = started.replace(tzinfo=timezone.utc)
    # every started minute counts: 61 seconds = 2 minutes
    minutes = max(1, math.ceil((now - started).total_seconds() / 60))
    rental.stopped_at = now
    rental.total_minutes = minutes
    rental.price_eur = calculate_price(minutes)
    db.commit()
    REVENUE.inc(rental.price_eur)
    return {"rental_id": rental.id, "duration_min": minutes, "price_eur": rental.price_eur}


# only the rentals of the caller (user id chosen by the gateway, not by the client)
@app.get("/rentals", tags=["rentals"])
def my_rentals(db: Session = Depends(get_db), x_user_id: int = Header()):
    rentals = db.scalars(select(Rental).where(Rental.user_id == x_user_id)
                         .order_by(Rental.id)).all()
    return [{"rental_id": r.id, "bike_id": r.bike_id, "started_at": r.started_at,
             "stopped_at": r.stopped_at, "price_eur": r.price_eur} for r in rentals]


# Target of the Location header. Declared last so that "/rentals/health" is matched first.
@app.get("/rentals/{rental_id}", tags=["rentals"])
def get_rental(rental_id: int, db: Session = Depends(get_db), x_user_id: int = Header()):
    rental = db.get(Rental, rental_id)
    if rental is None or rental.user_id != x_user_id:   # same rule as stop: only your own rental
        raise HTTPException(status_code=404, detail="Rental not found")
    return {"rental_id": rental.id, "bike_id": rental.bike_id, "started_at": rental.started_at,
            "stopped_at": rental.stopped_at, "price_eur": rental.price_eur}
