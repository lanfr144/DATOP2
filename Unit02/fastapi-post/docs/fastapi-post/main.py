from typing import Optional, List
from fastapi import FastAPI, HTTPException, Query, Depends, BackgroundTasks, status
from pydantic import BaseModel, Field

app = FastAPI(title="FastAPI Lab 2")

# ------- Pydantic models -----
class ItemIn(BaseModel):
    name: str = Field(..., min_length=2, max_length=64)
    price: float = Field(..., ge=0)
    tags: List[str] = Field(default_factory=list)
    rating: Optional[float] = Field(None, ge=0, le=5)
    # old (v1 style):
    # sizes: Optional[conlist(int, min_items=1, max_items=5)] = None
    # new (v2 style):
    sizes: Optional[List[int]] = Field(default=None, min_length=1, max_length=5)

class ItemOut(ItemIn):
    id: int

# ------- In-memory DB (for demo) -----
DB: List[ItemOut] = []

# ------- Dependency example -----
def pagination(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    return {"limit": limit, "offset": offset}

# ------- Background task -----
def log_creation(item_id: int):
    # pretend to write to a log/queue
    print(f"[bg] Item created: {item_id}")

# ----- Routes -----
@app.get("/", tags=["health"])
def root():
    return {"ok": True}

@app.post(
    "/items",
    response_model=ItemOut,
    status_code=status.HTTP_201_CREATED,
    tags=["items"],
)
def create_item(payload: ItemIn, bg: BackgroundTasks):
    item_id = len(DB) + 1
    item = ItemOut(id=item_id, **payload.model_dump())
    DB.append(item)
    bg.add_task(log_creation, item_id)
    return item

@app.get("/items/{item_id}", response_model=ItemOut, tags=["items"])
def get_item(item_id: int):
    for it in DB:
        if it.id == item_id:
            return it
    raise HTTPException(status_code=404, detail="Item not found")

@app.get("/items", response_model=List[ItemOut], tags=["items"])
def list_items(p: dict = Depends(pagination), tag: Optional[str] = None):
    items = DB
    if tag:
        items = [i for i in items if tag in i.tags]
    start, end = p["offset"], p["offset"] + p["limit"]
    return items[start:end]


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["items"])
def delete_item(item_id: int):
    # find the item with this id in DB
    target_item = next((item for item in DB if item.id == item_id), None)
    
    # if not found, raise HTTPException(status_code=404, ...)
    if target_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Item not found")
    
    # remove it (DB.remove(...)) and return nothing
    DB.remove(target_item)
    return