import os

os.environ["DATABASE_URL"] = "sqlite:///./test.db"   # set BEFORE importing the app

from fastapi.testclient import TestClient  # noqa: E402

from app.db import Base, engine  # noqa: E402
from app.main import app  # noqa: E402

Base.metadata.drop_all(bind=engine)
USER = {"X-User-Id": "1"}          # in production this header is added by the gateway


def test_rental_flow():
    with TestClient(app) as client:
        r = client.post("/rentals/start", json={"bike_id": "BIKE-01"}, headers=USER)
        assert r.status_code == 201
        rid = r.json()["rental_id"]
        assert r.headers["location"] == f"/rentals/{rid}"
        assert client.get(r.headers["location"], headers=USER).status_code == 200
        assert client.get(r.headers["location"], headers={"X-User-Id": "2"}).status_code == 404
        other = client.post("/rentals/stop", json={"rental_id": rid}, headers={"X-User-Id": "2"})
        assert other.status_code == 404                     # not your rental
        stop = client.post("/rentals/stop", json={"rental_id": rid}, headers=USER)
        assert stop.json()["price_eur"] == 0.25


def test_user_header_required():
    with TestClient(app) as client:
        r = client.post("/rentals/start", json={"bike_id": "BIKE-02"})
        assert r.status_code == 422                         # X-User-Id missing


def test_metrics_exposed():
    with TestClient(app) as client:
        body = client.get("/metrics").text
        assert "rentals_started_total" in body and "http_requests_total" in body
