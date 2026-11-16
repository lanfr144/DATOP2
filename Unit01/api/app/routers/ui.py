"""
Pages HTML (Jinja2) : login, inscription, tableau de bord, documentation.

Ces routes ne sont pas incluses dans le schema OpenAPI (include_in_schema=False)
car ce ne sont pas des endpoints d'API mais des pages pour le navigateur.
"""
from pathlib import Path

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy.orm import Session

from .. import crud, models, schemas
from ..auth import authenticate_user, get_current_user, login_response, logout_response
from ..config import ADMIN_EMAIL
from ..database import get_db

router = APIRouter(include_in_schema=False)

# Correction : chemin absolu vers app/templates (avant : "templates", relatif au dossier
# courant, donc l'application plantait si on la lancait depuis un autre dossier).
templates = Jinja2Templates(directory=Path(__file__).resolve().parent.parent / "templates")


def _redirect(url: str) -> RedirectResponse:
    return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)


@router.get("/")
def root(user: models.User | None = Depends(get_current_user)):
    return _redirect("/dashboard" if user else "/login")


@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request, error: str | None = None,
               user: models.User | None = Depends(get_current_user)):
    if user:
        return _redirect("/dashboard")
    # Starlette recent : TemplateResponse(request, nom, contexte)
    return templates.TemplateResponse(request, "login.html", {"error": error})


@router.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...),
          db: Session = Depends(get_db)):
    # Le champ du formulaire s'appelle "username" (convention OAuth2) mais contient l'email.
    user = authenticate_user(db, email=username, password=password)
    if not user:
        return templates.TemplateResponse(
            request, "login.html", {"error": "Invalid credentials"},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    return login_response(user)


@router.get("/logout")
def logout():
    return logout_response()


@router.get("/register", response_class=HTMLResponse)
def register_form(request: Request, error: str | None = None):
    return templates.TemplateResponse(request, "register.html", {"error": error})


@router.post("/register")
def register(request: Request, name: str = Form(...), email: str = Form(...),
             password: str = Form(...), db: Session = Depends(get_db)):
    def form_error(message: str, code: int = 422):  # 422 = valeurs invalides (cf. cheat sheet)
        return templates.TemplateResponse(request, "register.html", {"error": message},
                                          status_code=code)

    # Validation avec le meme schema que l'API JSON (email valide, mot de passe >= 6 caracteres)
    try:
        new_user = schemas.UserCreate(name=name, email=email, password=password)
    except ValidationError as exc:
        return form_error("; ".join(err["msg"] for err in exc.errors()))
    if crud.get_user_by_email(db, email=new_user.email):
        return form_error("Email is already registered.", status.HTTP_409_CONFLICT)
    user = crud.create_user(db, new_user)
    return login_response(user)  # connexion automatique apres l'inscription


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, user: models.User | None = Depends(get_current_user),
              db: Session = Depends(get_db)):
    if not user:
        return _redirect("/login")
    # Seul l'administrateur voit la liste des utilisateurs
    users_preview = None
    if user.email.lower() == ADMIN_EMAIL.lower():
        users_preview = crud.get_users(db, skip=0, limit=50)
    return templates.TemplateResponse(request, "dashboard.html",
                                      {"user": user, "users_preview": users_preview})


@router.get("/docs", response_class=HTMLResponse)
def custom_docs(request: Request, user: models.User | None = Depends(get_current_user)):
    # Page /docs "maison" (avec menu) qui embarque le Swagger UI servi sur /swagger
    if not user:
        return _redirect("/login")
    return templates.TemplateResponse(request, "docs.html", {})
