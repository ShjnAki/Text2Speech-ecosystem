import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'bot'))

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from api_client import TTSApiClient, ApiClientError


@pytest.fixture
def client():
    return TTSApiClient(
        api_url="http://fake-api:8000",
        email="bot@test.com",
        password="secret"
    )


@pytest.mark.asyncio
async def test_login_stocke_le_token(client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"access_token": "jwt_token_123", "token_type": "bearer"}

    with patch.object(client._client, "post", new=AsyncMock(return_value=mock_response)):
        await client.login()

    assert client._token == "jwt_token_123"


@pytest.mark.asyncio
async def test_login_credentials_invalides_leve_erreur(client):
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"

    with patch.object(client._client, "post", new=AsyncMock(return_value=mock_response)):
        with pytest.raises(ApiClientError, match="Authentification échouée"):
            await client.login()


@pytest.mark.asyncio
async def test_tts_retourne_bytes_audio(client):
    client._token = "jwt_token_123"

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"fake_mp3_bytes"

    with patch.object(client._client, "post", new=AsyncMock(return_value=mock_response)):
        result = await client.tts("Bonjour")

    assert result == b"fake_mp3_bytes"


@pytest.mark.asyncio
async def test_tts_relogin_sur_401(client):
    client._token = "token_expiré"

    resp_401 = MagicMock()
    resp_401.status_code = 401

    resp_ok = MagicMock()
    resp_ok.status_code = 200
    resp_ok.content = b"audio_ok"

    login_resp = MagicMock()
    login_resp.status_code = 200
    login_resp.json.return_value = {"access_token": "nouveau_token", "token_type": "bearer"}

    call_count = 0

    async def fake_post(url, **kwargs):
        nonlocal call_count
        call_count += 1
        if "/tts" in url and call_count == 1:
            return resp_401
        if "/auth/login" in url:
            return login_resp
        return resp_ok

    with patch.object(client._client, "post", new=AsyncMock(side_effect=fake_post)):
        result = await client.tts("Bonjour")

    assert result == b"audio_ok"
    assert client._token == "nouveau_token"
