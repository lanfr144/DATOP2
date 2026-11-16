from pydantic import BaseModel, ConfigDict, Field


class BookIn(BaseModel):              # body of POST /books (all fields validated)
    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=120)
    stock: int = Field(default=0, ge=0)


class BookUpdate(BaseModel):          # every field optional: send only what changes
    title: str | None = Field(default=None, min_length=1, max_length=200)
    author: str | None = Field(default=None, min_length=1, max_length=120)
    stock: int | None = Field(default=None, ge=0)


class BookOut(BookIn):
    model_config = ConfigDict(from_attributes=True)   # read from SQLAlchemy objects
    id: int


class RentalStart(BaseModel):
    bike_id: str = Field(pattern=r"^BIKE-\d{2,}$")    # e.g. BIKE-01


class RentalStop(BaseModel):
    rental_id: int
