"""
API REST JSON pour les utilisateurs.

Note : pour le lab, ces endpoints ne sont pas proteges. En production, il faudrait
au minimum exiger un utilisateur connecte (Depends(get_current_user)) pour les lire.
"""
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, response: Response, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, email=user.email):
        # 409 Conflict (cheat sheet Unit 04bis) : la requete est valide mais entre en conflit
        # avec l'etat du serveur. 400 = "je ne peux pas lire la requete", 422 = valeurs invalides.
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    db_user = crud.create_user(db, user=user)
    response.headers["Location"] = f"/users/{db_user.id}"   # 201 + Location
    return db_user


@router.get("", response_model=list[schemas.UserRead])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_users(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=schemas.UserRead)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
