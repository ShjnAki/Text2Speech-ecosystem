import json
import os
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthError(Exception):
    pass


def _load_users() -> list[dict]:
    """Charge la liste des utilisateurs depuis la variable d'environnement USERS."""
    raw = os.getenv("USERS", "[]")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        raise AuthError("Variable d'environnement USERS invalide (JSON malformé)")


def verify_user(email: str, password: str) -> bool:
    """Vérifie email + mot de passe. Retourne True si valides."""
    users = _load_users()
    for user in users:
        if user["email"] == email:
            return pwd_context.verify(password, user["password_hash"])
    return False


def _get_jwt_secret() -> str:
    """Retourne le secret JWT ou lève AuthError si absent ou trop court (< 32 chars)."""
    secret = os.getenv("JWT_SECRET")
    if not secret or len(secret) < 32:
        raise AuthError("JWT_SECRET non configuré ou trop court (minimum 32 caractères)")
    return secret


def create_access_token(email: str) -> str:
    """Crée un JWT signé pour l'utilisateur donné."""
    secret = _get_jwt_secret()
    expire_days = int(os.getenv("JWT_EXPIRE_DAYS", "7"))
    expire = datetime.now(timezone.utc) + timedelta(days=expire_days)
    payload = {"sub": email, "exp": expire}
    return jwt.encode(payload, secret, algorithm="HS256")


def decode_access_token(token: str) -> dict:
    """Décode et valide un JWT. Lève AuthError si invalide ou expiré."""
    secret = _get_jwt_secret()
    try:
        return jwt.decode(token, secret, algorithms=["HS256"])
    except JWTError as e:
        raise AuthError(f"Token invalide ou expiré : {e}")
