import pytest
from httpx import AsyncClient, ASGITransport
from main import app, DB

@pytest.fixture(autouse=True)
def clear_db():
    DB.clear() # every test starts with an empty "database" 

@pytest.mark.asyncio
async def test_create_and_get_item():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
         # create
         payload = {
            "name": "Banana", 
            "price": 1.2, 
            "tags": ["fruit"], 
            "rating": 4.0
            } 
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

