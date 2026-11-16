"""Tests des endpoints du lab 02a (main.py + challenges de lab2a.py). Lancer : pytest -q (depuis api/)."""
from fastapi.testclient import TestClient

from app.lab2a import app as lab_app
from app.main import app as course_app

course = TestClient(course_app)
lab = TestClient(lab_app)


def test_course_endpoints():
    assert course.get("/").json() == {"message": "Hello, FastAPI!"}
    assert course.get("/hello/Ana").json() == {"greeting": "Hello, Ana!"}
    assert course.get("/hello/").status_code == 404                # nom manquant (Step 6)
    # "Your turn" : l'espace est encode %20 par le navigateur, FastAPI le decode
    assert course.get("/hello/Ada%20Lovelace").json() == {"greeting": "Hello, Ada Lovelace!"}
    assert course.get("/items/5").json() == {"item_id": 5, "q": None}   # cours Unit 02, p. 4
    assert course.get("/items/42", params={"q": "x"}).json() == {"item_id": 42, "q": "x"}
    assert course.get("/items/abd").status_code == 422          # pas un entier
    r = course.post("/items/", json={"name": "Pen", "price": 1.5})
    assert r.json() == {"received_item": {"name": "Pen", "price": 1.5, "in_stock": True}}
    # cours Unit 02, p. 4 : {"name": "Laptop", "price": "cheap"} -> 422
    assert course.post("/items/", json={"name": "Laptop", "price": "cheap"}).status_code == 422


def test_challenge_1_2_add():
    assert lab.get("/add", params={"a": 3, "b": 4}).json() == {"result": 7}
    r = lab.get("/add", params={"a": 3, "b": "abc"})             # challenge 2
    assert r.status_code == 422
    assert r.json()["detail"][0]["loc"] == ["query", "b"]


def test_challenge_3_square():
    assert lab.get("/square/9").json() == {"n": 9, "square": 81}


def test_challenge_4_title_version():
    info = lab.get("/openapi.json").json()["info"]
    assert info["title"] == "My First API" and info["version"] == "1.0.0"


def test_challenge_5_hello_lang():
    assert lab.get("/hello/Ana", params={"lang": "fr"}).json() == {"greeting": "Bonjour, Ana!"}
    assert lab.get("/hello/Ana", params={"lang": "de"}).json() == {"greeting": "Hallo, Ana!"}
    assert lab.get("/hello/Ana").json() == {"greeting": "Hello, Ana!"}
