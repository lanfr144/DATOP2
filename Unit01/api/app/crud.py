"""
Acces aux donnees (Create / Read) pour la table users.

Correction : ce fichier contenait par erreur une copie de main.py
(import circulaire "from . import crud" dans crud.py lui-meme).
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models, schemas
from .utils import get_password_hash


def get_user(db: Session, user_id: int) -> models.User | None:
    return db.get(models.User, user_id)


def get_user_by_email(db: Session, email: str) -> models.User | None:
    # Comparaison insensible a la casse : "Admin@Example.com" == "admin@example.com"
    return db.scalar(select(models.User).where(models.User.email == email.lower()))


def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[models.User]:
    return list(db.scalars(select(models.User).order_by(models.User.id).offset(skip).limit(limit)))


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    db_user = models.User(
        name=user.name,
        email=user.email.lower(),
        hashed_password=get_password_hash(user.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)  # recharge l'objet pour obtenir l'id genere par la base
    return db_user
