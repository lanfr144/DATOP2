"""Tables SQLAlchemy (ORM)."""
from sqlalchemy import Column, Integer, String

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    email = Column(String(256), unique=True, nullable=False, index=True)
    # On ne stocke JAMAIS le mot de passe en clair : seulement son hash bcrypt.
    hashed_password = Column(String(256), nullable=False)
