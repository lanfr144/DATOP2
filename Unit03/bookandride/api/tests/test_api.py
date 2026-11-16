import os

os.environ["DATABASE_URL"] = "sqlite:///./test.db"   # must be set BEFORE importing the app

from fastapi.testclient import TestClient  # noqa: E402

from app.db import Base, engine  # noqa: E402
from app.main import app  # noqa: E402

Base.metadata.drop_all(bind=engine)   # every run starts with empty tables


def test_health():
    with TestClient(app) as client:
        assert client.get("/health").json()["status"] == "ok"


def test_books_crud():
    with TestClient(app) as client:
        r = client.post("/books", json={"title": "Dune", "author": "Frank Herbert", "stock": 5})
        assert r.status_code == 201
        book_id = r.json()["id"]
        assert r.headers["location"] == f"/books/{book_id}"          # 201 + Location
        assert client.get("/books", params={"search": "herbert"}).json()[0]["title"] == "Dune"
        assert client.get("/books", params={"author": "herbert"}).json()[0]["title"] == "Dune"
        assert client.get("/books", params={"author": "dune"}).json() == []   # author only
        assert client.put(f"/books/{book_id}", json={"stock": 10}).json()["stock"] == 10
        assert client.delete(f"/books/{book_id}").status_code == 204
        assert client.get(f"/books/{book_id}").status_code == 404
        # validation: empty title and negative stock -> 422 with two errors
        r = client.post("/books", json={"title": "", "author": "X", "stock": -1})
        assert r.status_code == 422 and len(r.json()["detail"]) == 2


def test_rental_flow():
    with TestClient(app) as client:
        r = client.post("/rentals/start", json={"bike_id": "BIKE-01"})
        assert r.status_code == 201
        rid = r.json()["rental_id"]
        assert client.get(r.headers["location"]).json()["bike_id"] == "BIKE-01"
        assert client.post("/rentals/start", json={"bike_id": "BIKE-01"}).status_code == 409
        stop = client.post("/rentals/stop", json={"rental_id": rid}).json()
        assert stop == {"rental_id": rid, "duration_min": 1, "price_eur": 0.25}
        assert client.post("/rentals/stop", json={"rental_id": rid}).status_code == 409
        assert client.post("/rentals/start", json={"bike_id": "bike-1"}).status_code == 422


def test_my_rentals():
    with TestClient(app) as client:
        client.post("/rentals/start", json={"bike_id": "BIKE-42"}, headers={"X-User-Id": "7"})
        mine = client.get("/rentals/me", headers={"X-User-Id": "7"}).json()
        assert [r["bike_id"] for r in mine] == ["BIKE-42"]
        assert client.get("/rentals/999999").status_code == 404


def test_daily_cap_on_a_long_rental():
    """Stretch goal: a rental of 1 day + 1 minute costs 12.25 (not 12.00)."""
    from datetime import datetime, timedelta, timezone

    from app.db import SessionLocal
    from app.models import Rental

    with TestClient(app) as client:
        rid = client.post("/rentals/start", json={"bike_id": "BIKE-77"}).json()["rental_id"]
        with SessionLocal() as db:               # pretend the rental started 24 h + 30 s ago
            db.get(Rental, rid).started_at = datetime.now(timezone.utc) - timedelta(days=1, seconds=30)
            db.commit()
        stop = client.post("/rentals/stop", json={"rental_id": rid}).json()
        assert stop["duration_min"] == 24 * 60 + 1 and stop["price_eur"] == 12.25
