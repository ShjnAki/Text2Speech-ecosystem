# TTS Bot Telegram + Discord — Plan d'implémentation

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bot Python unique qui écoute sur Telegram et Discord, accepte du texte ou des fichiers `.txt`/`.md`, appelle l'API TTS locale, et retourne le fichier MP3 — avec ré-authentification automatique sur expiration de token.

**Architecture:** Deux bots (Telegram via `python-telegram-bot`, Discord via `discord.py`) tournent en parallèle dans le même processus grâce à `asyncio`. Un client HTTP partagé (`TTSApiClient`) gère le token JWT et se reconnecte automatiquement si le serveur renvoie 401.

**Tech Stack:** Python 3.11+, python-telegram-bot 21+, discord.py 2+, httpx (async), python-dotenv

**Prérequis :** L'API REST (plan `2026-06-04-api-rest.md`) doit être déployée et accessible à `TTS_API_URL`.

---

## Structure des fichiers

```
bot/
├── main.py          # Point d'entrée : lance Telegram + Discord en parallèle
├── api_client.py    # Client HTTP vers l'API TTS (auth + tts, gestion 401)
├── file_reader.py   # Lecture de fichiers .txt/.md depuis bytes
├── telegram_bot.py  # Handlers Telegram (texte + document)
├── discord_bot.py   # Handlers Discord (message + pièce jointe)
├── .env.example
├── requirements.txt
└── tts-bot.service

tests/
├── test_file_reader.py   # Tests lecture de fichiers
└── test_api_client.py    # Tests client HTTP (avec mocks)
```

---

## Tâche 1 : Scaffolding

**Fichiers :**
- Créer : `bot/requirements.txt`
- Créer : `bot/.env.example`

- [ ] **Étape 1 : Créer `bot/requirements.txt`**

```
python-telegram-bot==21.3
discord.py==2.3.2
httpx==0.27.0
python-dotenv==1.0.1
pytest==8.2.0
pytest-asyncio==0.23.6
```

- [ ] **Étape 2 : Créer `bot/.env.example`**

```ini
TELEGRAM_TOKEN=votre_token_telegram_botfather
DISCORD_TOKEN=votre_token_discord_application
TTS_API_URL=http://localhost:8000
# Compte dédié au bot — créer avec : python ../api/create_user.py bot@internal.local motdepasse
BOT_EMAIL=bot@internal.local
BOT_PASSWORD=motdepasse_bot_fort
```

- [ ] **Étape 3 : Installer dans un venv**

```bash
cd bot && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
```

- [ ] **Étape 4 : Commit**

```bash
git add bot/requirements.txt bot/.env.example
git commit -m "chore(bot): scaffolding dépendances et env example"
```

---

## Tâche 2 : Lecteur de fichiers

**Fichiers :**
- Créer : `bot/file_reader.py`
- Créer : `tests/test_file_reader.py`

- [ ] **Étape 1 : Écrire les tests**

Créer `tests/test_file_reader.py` :

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'bot'))

from file_reader import read_file, FileReaderError
import pytest


def test_lit_fichier_txt():
    contenu = b"Bonjour le monde"
    assert read_file(contenu, "texte.txt") == "Bonjour le monde"


def test_lit_fichier_md():
    contenu = b"# Titre\nDu contenu"
    assert read_file(contenu, "doc.md") == "# Titre\nDu contenu"


def test_lit_fichier_utf8():
    contenu = "Texte avec accents éàü".encode("utf-8")
    assert read_file(contenu, "test.txt") == "Texte avec accents éàü"


def test_extension_non_supportee_leve_erreur():
    with pytest.raises(FileReaderError, match="non supporté"):
        read_file(b"data", "fichier.pdf")


def test_fichier_vide_leve_erreur():
    with pytest.raises(FileReaderError, match="vide"):
        read_file(b"", "vide.txt")
```

- [ ] **Étape 2 : Vérifier échec**

```bash
cd bot && source .venv/bin/activate && pytest ../tests/test_file_reader.py -v
```

Attendu : `ImportError: No module named 'file_reader'`.

- [ ] **Étape 3 : Implémenter `bot/file_reader.py`**

```python
EXTENSIONS_SUPPORTEES = {".txt", ".md"}


class FileReaderError(Exception):
    pass


def read_file(content: bytes, filename: str) -> str:
    """Lit le contenu d'un fichier .txt ou .md et retourne le texte."""
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if ext not in EXTENSIONS_SUPPORTEES:
        raise FileReaderError(
            f"Format de fichier non supporté : '{ext}'. "
            f"Formats acceptés : {', '.join(EXTENSIONS_SUPPORTEES)}"
        )

    if not content:
        raise FileReaderError("Le fichier est vide.")

    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        return content.decode("latin-1")
```

- [ ] **Étape 4 : Relancer les tests**

```bash
pytest ../tests/test_file_reader.py -v
```

Attendu : tous `PASSED`.

- [ ] **Étape 5 : Commit**

```bash
git add bot/file_reader.py tests/test_file_reader.py
git commit -m "feat(bot): lecteur de fichiers .txt/.md avec tests"
```

---

## Tâche 3 : Client HTTP vers l'API TTS

**Fichiers :**
- Créer : `bot/api_client.py`
- Créer : `tests/test_api_client.py`

- [ ] **Étape 1 : Écrire les tests**

Créer `tests/test_api_client.py` :

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'bot'))

import pytest
import httpx
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

    # Premier appel : 401 → doit relogin puis réessayer
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
```

- [ ] **Étape 2 : Vérifier échec**

```bash
pytest ../tests/test_api_client.py -v
```

Attendu : `ImportError: No module named 'api_client'`.

- [ ] **Étape 3 : Implémenter `bot/api_client.py`**

```python
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
```

- [ ] **Étape 4 : Relancer les tests**

```bash
pytest ../tests/test_api_client.py -v
```

Attendu : tous `PASSED`.

- [ ] **Étape 5 : Commit**

```bash
git add bot/api_client.py tests/test_api_client.py
git commit -m "feat(bot): client HTTP TTS avec gestion JWT et relogin auto sur 401"
```

---

## Tâche 4 : Bot Telegram

**Fichiers :**
- Créer : `bot/telegram_bot.py`

- [ ] **Étape 1 : Implémenter `bot/telegram_bot.py`**

```python
"""Bot Telegram TTS — utilise python-telegram-bot 21+."""
import io
import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from api_client import TTSApiClient, ApiClientError
from file_reader import read_file, FileReaderError

logger = logging.getLogger(__name__)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Bonjour ! Envoyez-moi du texte ou un fichier .txt/.md "
        "et je vous retournerai la version audio."
    )


async def handle_texte(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Traite un message texte et retourne le MP3."""
    client: TTSApiClient = context.bot_data["api_client"]
    texte = update.message.text

    msg = await update.message.reply_text("Génération en cours...")
    try:
        audio_bytes = await client.tts(texte)
        await update.message.reply_audio(
            audio=io.BytesIO(audio_bytes),
            filename="audio.mp3",
            title="TTS Audio",
        )
    except ApiClientError as e:
        await update.message.reply_text(f"Erreur : {e}")
    finally:
        await msg.delete()


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Traite un fichier .txt ou .md joint et retourne le MP3."""
    client: TTSApiClient = context.bot_data["api_client"]
    doc = update.message.document

    msg = await update.message.reply_text("Lecture du fichier en cours...")
    try:
        file = await context.bot.get_file(doc.file_id)
        file_bytes = await file.download_as_bytearray()
        texte = read_file(bytes(file_bytes), doc.file_name)
    except FileReaderError as e:
        await msg.edit_text(f"Erreur de lecture : {e}")
        return

    await msg.edit_text("Génération audio en cours...")
    try:
        audio_bytes = await client.tts(texte)
        await update.message.reply_audio(
            audio=io.BytesIO(audio_bytes),
            filename="audio.mp3",
            title="TTS Audio",
        )
    except ApiClientError as e:
        await update.message.reply_text(f"Erreur API : {e}")
    finally:
        await msg.delete()


def create_telegram_app(token: str, api_client: TTSApiClient) -> Application:
    """Crée et configure l'application Telegram."""
    app = Application.builder().token(token).build()
    app.bot_data["api_client"] = api_client

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_texte))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    return app
```

- [ ] **Étape 2 : Commit**

```bash
git add bot/telegram_bot.py
git commit -m "feat(bot): handlers Telegram texte et fichier .txt/.md"
```

---

## Tâche 5 : Bot Discord

**Fichiers :**
- Créer : `bot/discord_bot.py`

- [ ] **Étape 1 : Implémenter `bot/discord_bot.py`**

```python
"""Bot Discord TTS — utilise discord.py 2+."""
import io
import logging

import discord

from api_client import TTSApiClient, ApiClientError
from file_reader import read_file, FileReaderError

logger = logging.getLogger(__name__)

# Préfixe de commande pour éviter de traiter tous les messages
COMMANDE_PREFIX = "!tts"


class TTSDiscordBot(discord.Client):
    def __init__(self, api_client: TTSApiClient, **kwargs):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents, **kwargs)
        self.api_client = api_client

    async def on_ready(self):
        logger.info(f"Bot Discord connecté en tant que {self.user}")

    async def on_message(self, message: discord.Message):
        # Ignorer les messages du bot lui-même
        if message.author == self.user:
            return

        texte = None

        # Cas 1 : pièce jointe .txt ou .md
        if message.attachments:
            for attachment in message.attachments:
                if attachment.filename.lower().endswith((".txt", ".md")):
                    try:
                        file_bytes = await attachment.read()
                        texte = read_file(file_bytes, attachment.filename)
                        break
                    except FileReaderError as e:
                        await message.channel.send(f"Erreur de lecture : {e}")
                        return

        # Cas 2 : commande texte "!tts <texte>"
        elif message.content.startswith(COMMANDE_PREFIX):
            texte = message.content[len(COMMANDE_PREFIX):].strip()
            if not texte:
                await message.channel.send(
                    f"Usage : `{COMMANDE_PREFIX} Texte à lire` "
                    "ou joindre un fichier .txt/.md"
                )
                return

        # Si aucun texte identifié, ignorer
        if texte is None:
            return

        msg = await message.channel.send("Génération audio en cours...")
        try:
            audio_bytes = await self.api_client.tts(texte)
            await message.channel.send(
                file=discord.File(io.BytesIO(audio_bytes), filename="audio.mp3")
            )
            await msg.delete()
        except ApiClientError as e:
            await msg.edit(content=f"Erreur API : {e}")
```

- [ ] **Étape 2 : Commit**

```bash
git add bot/discord_bot.py
git commit -m "feat(bot): handler Discord avec commande !tts et pièces jointes"
```

---

## Tâche 6 : Point d'entrée principal

**Fichiers :**
- Créer : `bot/main.py`

- [ ] **Étape 1 : Implémenter `bot/main.py`**

```python
"""
Bot TTS — Telegram + Discord
=============================
Lance les deux bots en parallèle via asyncio.

Démarrage manuel (dev) :
    cd bot && source .venv/bin/activate
    python main.py

Démarrage production (systemd) :
    sudo systemctl start tts-bot
"""
import asyncio
import logging
import os

from dotenv import load_dotenv

load_dotenv()

from api_client import TTSApiClient
from telegram_bot import create_telegram_app
from discord_bot import TTSDiscordBot

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    # Vérification des variables d'environnement requises
    required_vars = ["TELEGRAM_TOKEN", "DISCORD_TOKEN", "TTS_API_URL", "BOT_EMAIL", "BOT_PASSWORD"]
    for var in required_vars:
        if not os.getenv(var):
            raise EnvironmentError(f"Variable d'environnement manquante : {var}")

    # Client partagé entre les deux bots
    api_client = TTSApiClient(
        api_url=os.getenv("TTS_API_URL"),
        email=os.getenv("BOT_EMAIL"),
        password=os.getenv("BOT_PASSWORD"),
    )

    # Authentification initiale
    logger.info("Authentification auprès de l'API TTS...")
    await api_client.login()
    logger.info("Token JWT obtenu.")

    # Initialisation des bots
    telegram_app = create_telegram_app(os.getenv("TELEGRAM_TOKEN"), api_client)
    discord_client = TTSDiscordBot(api_client=api_client)

    # Lancement en parallèle
    async with telegram_app:
        await telegram_app.initialize()
        await telegram_app.start()
        await telegram_app.updater.start_polling(drop_pending_updates=True)
        logger.info("Bot Telegram démarré.")

        logger.info("Bot Discord démarré.")
        try:
            await discord_client.start(os.getenv("DISCORD_TOKEN"))
        finally:
            await telegram_app.updater.stop()
            await telegram_app.stop()
            await api_client.close()


if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **Étape 2 : Commit**

```bash
git add bot/main.py
git commit -m "feat(bot): point d'entrée principal Telegram + Discord en parallèle"
```

---

## Tâche 7 : Service systemd

**Fichiers :**
- Créer : `bot/tts-bot.service`

- [ ] **Étape 1 : Créer `bot/tts-bot.service`**

```ini
[Unit]
Description=TTS Bot Telegram + Discord
After=network.target
# Démarrer après l'API TTS si elle tourne sur la même machine
After=tts-api.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/tts-ecosystem/bot
EnvironmentFile=/opt/tts-ecosystem/bot/.env
ExecStart=/opt/tts-ecosystem/bot/.venv/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

- [ ] **Étape 2 : Instructions de déploiement**

```bash
# Sur le VPS — après avoir déployé l'API :
cd /opt/tts-ecosystem/bot
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env && nano .env   # Remplir les tokens Telegram/Discord

sudo cp tts-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable tts-bot
sudo systemctl start tts-bot
sudo journalctl -u tts-bot -f
```

- [ ] **Étape 3 : Commit**

```bash
git add bot/tts-bot.service
git commit -m "chore(bot): service systemd pour déploiement VPS"
```

---

## Vérification finale (self-review)

- [x] Spec coverage : Telegram + Discord en parallèle, fichiers .txt/.md, login au démarrage, relogin sur 401, message d'erreur explicite, tts-bot.service
- [x] Pas de placeholders
- [x] Types cohérents : `TTSApiClient`, `ApiClientError`, `FileReaderError` cohérents entre tous les fichiers
