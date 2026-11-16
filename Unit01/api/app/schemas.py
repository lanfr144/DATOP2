"""
Schemas Pydantic : forme du JSON qui entre (UserCreate) et qui sort (UserRead).

Correction : ce fichier contenait par erreur une copie de utils.py (hash/JWT).
"""
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    email: EmailStr  # valide le format de l'adresse (necessite email-validator)


class UserCreate(UserBase):
    # Mot de passe recu en clair uniquement a la creation, jamais renvoye.
    password: str = Field(min_length=6, max_length=128)


class UserRead(UserBase):
    # from_attributes : permet de construire le schema depuis un objet SQLAlchemy
    model_config = ConfigDict(from_attributes=True)
    id: int
