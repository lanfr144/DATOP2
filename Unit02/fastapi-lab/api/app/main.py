"""
Unit 02a - Premiere API FastAPI (version du cours, avant les challenges).

Correction : regroupe l'ancien Unit02/main.py ("Ma premiere API") et fastapi-lab/main.py
(/hello/{name}) ; l'import de BaseModel est remonte en haut du fichier (PEP 8).

Lancer (depuis api/) :  python -m app.main     ou   uvicorn app.main:app --reload --port <APP_PORT>
"""
from fastapi import FastAPI
from pydantic import BaseModel

from .config import APP_HOST, APP_PORT

app = FastAPI(
    title="Ma première API.",
    description="Cette API est développée dans le cadre du cours de dataop2 et retourne un message d'accueil.",
    version="1.0.0",
)


class Item(BaseModel):
    name: str
    price: float
    in_stock: bool = True  # optionnel, valeur par defaut


@app.get("/")
def root():
    """Premier endpoint : retourne {"message": "Hello, FastAPI!"}."""
    return {"message": "Hello, FastAPI!"}


@app.get("/hello/{name}")
def say_hello(name: str):
    """Parametre de chemin (path parameter) : /hello/Ana -> {"greeting": "Hello, Ana!"}."""
    return {"greeting": f"Hello, {name}!"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    """item_id = parametre de chemin (converti en int), q = parametre de requete optionnel."""
    return {"item_id": item_id, "q": q}


@app.post("/items/")
def create_item(item: Item):
    """Le corps JSON est valide par Pydantic (422 si price n'est pas un nombre)."""
    return {"received_item": item}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=APP_HOST, port=APP_PORT, reload=True)
