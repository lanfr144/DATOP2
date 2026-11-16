"""
Tests de l'API GESTEL avec une base SQLite temporaire (aucun MySQL necessaire).

Lancer depuis le dossier api/ :  pytest -q
"""
import os
import tempfile
from pathlib import Path

# A definir AVANT d'importer l'application (la config est lue a l'import).
_TMP_DB = Path(tempfile.gettempdir()) / "gestel_test.db"
_TMP_DB.unlink(missing_ok=True)
os.environ["DATABASE_URL"] = f"sqlite:///{_TMP_DB}"
os.environ["ADMIN_EMAIL"] = "admin@example.com"
os.environ["ADMIN_PASSWORD"] = "admin-test-pwd"

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


def test_healthy():
    with TestClient(app) as client:
        assert client.get("/healthy").json() == {"status": "ok"}


def test_users_crud():
    with TestClient(app) as client:
        r = client.post("/users", json={"name": "Alice", "email": "alice@example.com", "password": "secret1"})
        assert r.status_code == 201
        user = r.json()
        assert r.headers["location"] == f"/users/{user['id']}"
        assert "password" not in user and "hashed_password" not in user   # jamais renvoye
        assert client.get(f"/users/{user['id']}").json()["email"] == "alice@example.com"
        # doublon -> 409 Conflict, email invalide -> 422, inconnu -> 404
        assert client.post("/users", json={"name": "A", "email": "alice@example.com", "password": "secret1"}).status_code == 409
        assert client.post("/users", json={"name": "A", "email": "not-an-email", "password": "secret1"}).status_code == 422
        assert client.get("/users/99999").status_code == 404


def test_login_flow():
    with TestClient(app) as client:
        # non connecte -> redirection vers /login
        r = client.get("/dashboard", follow_redirects=False)
        assert r.status_code == 302 and r.headers["location"] == "/login"
        # mauvais mot de passe -> 401
        assert client.post("/login", data={"username": "admin@example.com", "password": "bad"}).status_code == 401
        # bon mot de passe -> cookie + dashboard admin avec la liste des utilisateurs
        r = client.post("/login", data={"username": "admin@example.com", "password": "admin-test-pwd"})
        assert r.status_code == 200 and "All users (preview)" in r.text
        # deconnexion -> cookie supprime
        client.get("/logout")
        assert client.get("/dashboard", follow_redirects=False).status_code == 302


def test_register():
    with TestClient(app) as client:
        r = client.post("/register", data={"name": "Bob", "email": "bob@example.com", "password": "bobpwd1"})
        assert r.status_code == 200 and "Welcome, Bob!" in r.text
        r = client.post("/register", data={"name": "Bob", "email": "bob@example.com", "password": "bobpwd1"})
        assert r.status_code == 409
        r = client.post("/register", data={"name": "Eve", "email": "not-an-email", "password": "evepwd1"})
        assert r.status_code == 422
