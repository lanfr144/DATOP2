"""
Outils de securite : hash des mots de passe (bcrypt) et jetons JWT.

Correction : passlib n'est plus maintenu et casse avec bcrypt >= 4.1 ;
on utilise directement la librairie bcrypt et PyJWT (au lieu de python-jose).
"""
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from .config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY


def _to_bytes(password: str) -> bytes:
    # bcrypt ne prend en compte que les 72 premiers octets (et bcrypt 5 refuse au-dela).
    return password.encode("utf-8")[:72]


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(_to_bytes(password), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(_to_bytes(plain_password), hashed_password.encode("utf-8"))
    except ValueError:  # hash invalide/corrompu en base
        return False


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    # datetime.utcnow() est deprecie depuis Python 3.12 : on utilise un datetime "aware" UTC
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Retourne le contenu du jeton, ou {} s'il est invalide ou expire."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return {}
