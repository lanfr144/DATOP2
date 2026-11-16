import os

os.environ["DATABASE_URL"] = "sqlite:///./test.db"   # must be set BEFORE importing the app

from fastapi.testclient import TestClient  # noqa: E402

from app.db import Base, engine  # noqa: E402
from app.main import app  # noqa: E402

Base.metadata.drop_all(bind=engine)


def test_books_crud():
    with TestClient(app) as client:
        r = client.post("/books", json={"title": "Dune", "author": "Frank Herbert", "stock": 5})
        assert r.status_code == 201
        book_id = r.json()["id"]
        assert r.headers["location"] == f"/books/{book_id}"
        assert client.get("/books", params={"search": "herbert"}).json()[0]["title"] == "Dune"
        assert client.put(f"/books/{book_id}", json={"stock": 10}).json()["stock"] == 10
        assert client.delete(f"/books/{book_id}").status_code == 204
        assert client.get(f"/books/{book_id}").status_code == 404


def test_rentals_are_gone_from_books_service():
    with TestClient(app) as client:
        assert client.post("/rentals/start", json={"bike_id": "BIKE-01"}).status_code == 404
