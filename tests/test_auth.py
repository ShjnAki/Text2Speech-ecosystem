import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))

import pytest
from unittest.mock import patch
from auth import verify_user, create_access_token, decode_access_token, AuthError

# Hash bcrypt de "motdepasse" généré avec passlib
HASH_MOTDEPASSE = "$2b$12$5FVE6b9cYyAwX3I1m4c7leNcrpVmd..wXV99fSZBtJ5k0vOEKqhNy"

FAKE_USERS = json.dumps([
    {"email": "test@example.com", "password_hash": HASH_MOTDEPASSE}
])


def test_verify_user_credentials_valides():
    with patch.dict(os.environ, {"USERS": FAKE_USERS}):
        assert verify_user("test@example.com", "motdepasse") is True


def test_verify_user_mauvais_mot_de_passe():
    with patch.dict(os.environ, {"USERS": FAKE_USERS}):
        assert verify_user("test@example.com", "mauvais") is False


def test_verify_user_email_inconnu():
    with patch.dict(os.environ, {"USERS": FAKE_USERS}):
        assert verify_user("inconnu@example.com", "motdepasse") is False


def test_create_et_decode_token():
    with patch.dict(os.environ, {"JWT_SECRET": "secret_test_32chars_padding_here", "JWT_EXPIRE_DAYS": "7"}):
        token = create_access_token("test@example.com")
        payload = decode_access_token(token)
        assert payload["sub"] == "test@example.com"


def test_decode_token_invalide_leve_erreur():
    with patch.dict(os.environ, {"JWT_SECRET": "secret_test_32chars_padding_here"}):
        with pytest.raises(AuthError):
            decode_access_token("token.invalide.ici")
