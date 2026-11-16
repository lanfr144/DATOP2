from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


# Unit 04: the Rental table moved to rentals-service (database per service)
class Book(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    author: Mapped[str] = mapped_column(String(120))
    stock: Mapped[int] = mapped_column(default=0)
