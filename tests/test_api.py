import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

HASH_MOTDEPASSE = "$2b$12$ZVL0pVu4.J3HYfL1BLCf3.DfEmS1plLqtPk6y2G7nu9oAZgkAxuRq"
FAKE_USERS = json.dumps([{"email": "test@example.com", "password_hash": HASH_MOTDEPASSE}])
FAKE_ENV = {
    "USERS": FAKE_USERS,
    "JWT_SECRET": "secret_test_32chars_padding_here_ok",
    "JWT_EXPIRE_DAYS": "7",
    "ELEVENLABS_API_KEY": "fake",
    "ELEVENLABS_VOICE_ID": "fake_voice",
    "TTS_API_PORT": "8000",
}


@pytest.fixture
def client():
    with patch.dict(os.environ, FAKE_ENV):
        import importlib
        import main as main_module
        importlib.reload(main_module)
        with TestClient(main_module.app) as c:
            yield c


def test_login_credentials_valides(client):
    response = client.post("/auth/login", json={"email": "test@example.com", "password": "motdepasse"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_credentials_invalides(client):
    response = client.post("/auth/login", json={"email": "test@example.com", "password": "mauvais"})
    assert response.status_code == 401


def test_tts_sans_token_retourne_401(client):
    response = client.post("/tts", json={"text": "Bonjour"})
    assert response.status_code == 401


def test_tts_avec_token_valide_appelle_elevenlabs(client):
    login_resp = client.post("/auth/login", json={"email": "test@example.com", "password": "motdepasse"})
    token = login_resp.json()["access_token"]

    with patch("main.generate_tts_audio", return_value=b"fake_mp3_bytes"):
        response = client.post(
            "/tts",
            json={"text": "Bonjour"},
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/mpeg"


def test_tts_texte_trop_long_retourne_400(client):
    login_resp = client.post("/auth/login", json={"email": "test@example.com", "password": "motdepasse"})
    token = login_resp.json()["access_token"]

    long_text = "A" * 2600
    with patch("tts.generate_tts_audio", side_effect=__import__('tts').TTSError("Texte trop long")):
        response = client.post(
            "/tts",
            json={"text": long_text},
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 400
