"""
Tests asynchrones du lab 02b (httpx.AsyncClient + ASGITransport : pas de vrai serveur).
Lancer depuis api/ :  pytest -q
"""
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import DB, app

@pytest.fixture(autouse=True)
def clear_db():
    DB.clear()  # every test starts with an empty "database"

@pytest.mark.asyncio
async def test_create_and_get_item():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # create
        payload = {"name": "Banana", "price": 1.2, "tags": ["fruit"], "rating": 4.0}
        r = await ac.post("/items", json=payload)
        assert r.status_code == 201
        data = r.json()
        assert data["id"] == 1
        assert data["name"] == "Banana"
        # get
        r2 = await ac.get("/items/1")
        assert r2.status_code == 200
        assert r2.json()["name"] == "Banana"

@pytest.mark.asyncio
async def test_validation_error():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/items", json={"name": "A", "price": 10})
        assert r.status_code == 422


@pytest.mark.asyncio
async def test_get_unknown_item_returns_404():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/items/99")
        assert r.status_code == 404
        assert r.json()["detail"] == "Item not found"


@pytest.mark.asyncio
async def test_negative_price_is_rejected():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/items", json={"name": "Apple", "price": -1})
        assert r.status_code == 422


@pytest.mark.asyncio
async def test_filter_by_tag():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        await ac.post("/items", json={"name": "Banana", "price": 1.2, "tags": ["fruit"]})
        await ac.post("/items", json={"name": "Carrot", "price": 0.8, "tags": ["vegetable"]})

        r = await ac.get("/items", params={"tag": "fruit"})
        assert r.status_code == 200
        items = r.json()
        assert len(items) == 1
        assert items[0]["name"] == "Banana"


@pytest.mark.asyncio
async def test_delete_item():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/items", json={"name": "Banana", "price": 1.2})
        assert r.status_code == 201
        item_id = r.json()["id"]

        # delete -> 204 No Content
        r_del = await ac.delete(f"/items/{item_id}")
        assert r_del.status_code == 204

        # item is gone -> 404
        r_get = await ac.get(f"/items/{item_id}")
        assert r_get.status_code == 404



@pytest.mark.asyncio
async def test_ids_are_not_reused_after_delete():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        id1 = (await ac.post("/items", json={"name": "One", "price": 1})).json()["id"]
        id2 = (await ac.post("/items", json={"name": "Two", "price": 2})).json()["id"]
        await ac.delete(f"/items/{id1}")
        id3 = (await ac.post("/items", json={"name": "Three", "price": 3})).json()["id"]
        assert id3 not in (id1, id2)


@pytest.mark.asyncio
async def test_pagination_limits():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        for i in range(5):
            await ac.post("/items", json={"name": f"Item{i}", "price": i})
        r = await ac.get("/items", params={"limit": 2, "offset": 1})
        assert [it["name"] for it in r.json()] == ["Item1", "Item2"]
        assert (await ac.get("/items", params={"limit": 0})).status_code == 422   # ge=1


# ---------- "Your turn" du sujet : predire le code de statut ----------
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload",
    [
        {"name": "Shoe", "price": 10, "rating": 6},                     # le > 5
        {"name": "Shoe", "price": 10, "sizes": [1, 2, 3, 4, 5, 6]},     # max_length=5
        {"name": "Shoe", "price": "cheap"},                             # pas un nombre
    ],
)
async def test_your_turn_invalid_payloads_return_422(payload):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        assert (await ac.post("/items", json=payload)).status_code == 422


@pytest.mark.asyncio
async def test_your_turn_curl_example_running_shoes():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {"name": "Running Shoes", "price": 89.9, "tags": ["sport", "shoes"],
                   "rating": 4.5, "sizes": [40, 41, 42]}
        r = await ac.post("/items", json=payload)
        assert r.status_code == 201 and r.json() == {**payload, "id": 1}
        r = await ac.get("/items", params={"limit": 1, "offset": 0, "tag": "shoes"})
        assert [it["name"] for it in r.json()] == ["Running Shoes"]


# ---------- Tip du sujet : le client de test synchrone ----------
def test_root():
    from fastapi.testclient import TestClient

    client = TestClient(app)
    r = client.get("/")
    assert r.status_code == 200
    assert r.json() == {"ok": True}
