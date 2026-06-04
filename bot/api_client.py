import httpx


class ApiClientError(Exception):
    pass


class TTSApiClient:
    """
    Client async vers l'API TTS.
    Gère l'authentification JWT et le renouvellement automatique du token.
    """

    def __init__(self, api_url: str, email: str, password: str):
        self._api_url = api_url.rstrip("/")
        self._email = email
        self._password = password
        self._token: str | None = None
        self._client = httpx.AsyncClient(timeout=60.0)

    async def login(self) -> None:
        """Authentifie le bot et stocke le token JWT en mémoire."""
        response = await self._client.post(
            f"{self._api_url}/auth/login",
            json={"email": self._email, "password": self._password},
        )
        if response.status_code != 200:
            raise ApiClientError(
                f"Authentification échouée (HTTP {response.status_code}). "
                "Vérifiez BOT_EMAIL et BOT_PASSWORD dans .env."
            )
        self._token = response.json()["access_token"]

    async def tts(self, text: str) -> bytes:
        """
        Envoie le texte à l'API TTS et retourne les bytes MP3.
        Relance un login automatique si le token est expiré (401).
        """
        if self._token is None:
            await self.login()

        response = await self._client.post(
            f"{self._api_url}/tts",
            json={"text": text},
            headers={"Authorization": f"Bearer {self._token}"},
        )

        if response.status_code == 401:
            # Token expiré → renouvellement automatique
            await self.login()
            response = await self._client.post(
                f"{self._api_url}/tts",
                json={"text": text},
                headers={"Authorization": f"Bearer {self._token}"},
            )

        if response.status_code == 400:
            raise ApiClientError(response.json().get("detail", "Erreur 400"))

        if response.status_code != 200:
            raise ApiClientError(f"Erreur API TTS (HTTP {response.status_code})")

        return response.content

    async def close(self) -> None:
        await self._client.aclose()
