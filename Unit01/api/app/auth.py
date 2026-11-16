"""
Authentification par cookie HTTP-only contenant un JWT.

Flux : POST /login -> verification bcrypt -> cookie "access_token" -> redirection /dashboard.
"""
from fastapi import Depends, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from . import crud, models
from .config import ACCESS_TOKEN_EXPIRE_MINUTES
from .database import get_db
from .utils import create_access_token, decode_access_token, verify_password

COOKIE_NAME = "access_token"


def authenticate_user(db: Session, email: str, password: str) -> models.User | None:
    """Retourne l'utilisateur si email + mot de passe sont corrects, sinon None."""
    user = crud.get_user_by_email(db, email=email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def get_current_user(request: Request, db: Session = Depends(get_db)) -> models.User | None:
    """Dependance FastAPI : lit le cookie et retourne l'utilisateur connecte (ou None)."""
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    email = decode_access_token(token).get("sub")
    if not email:
        return None
    return crud.get_user_by_email(db, email=email)


def login_response(user: models.User) -> RedirectResponse:
    """Cree le JWT, le place dans un cookie et redirige vers le tableau de bord."""
    access_token = create_access_token(data={"sub": user.email})
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    # httponly : le cookie n'est pas lisible en JavaScript (protection contre le vol par XSS)
    # samesite=lax : limite l'envoi du cookie depuis d'autres sites (protection CSRF de base)
    response.set_cookie(
        COOKIE_NAME,
        access_token,
        httponly=True,
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    return response


def logout_response() -> RedirectResponse:
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(COOKIE_NAME)
    return response
