# TTS Ecosystem

A multi-platform Text-to-Speech system made up of three independent modules: a REST API, messaging bots, and an Android mobile app.

```
┌─────────────┐     JWT      ┌──────────────────────────────┐
│  Mobile     │ ──────────► │                              │
│  (Android)  │             │   REST API (FastAPI)         │
└─────────────┘             │   Google Cloud TTS           │
                             │                              │
┌─────────────┐     JWT      │   VPS Contabo (Debian)       │
│  Bot        │ ──────────► │   systemd + Nginx + HTTPS    │
│  Telegram   │             │                              │
│  Discord    │             └──────────────────────────────┘
└─────────────┘
```

## Features

- **JWT authentication** — email/password login, token valid for 7 days
- **Text-to-speech** — text → MP3 conversion via Google Cloud TTS (French neural voice)
- **Telegram & Discord bots** — accept plain text or `.txt`/`.md` files, return an MP3
- **Android app** — direct text input, built-in audio playback, 5,000-character limit
- **Markdown stripping** — Markdown syntax is removed before synthesis

---

## Project structure

```
tts-ecosystem/
├── api/          # FastAPI REST API
├── bot/          # Telegram + Discord bots
├── mobile/       # Android app (Capacitor)
└── tests/        # Unit tests (pytest)
```

---

## Tech stack

### API (`api/`)

| Component | Technology |
|-----------|------------|
| Framework | FastAPI 0.111 + Uvicorn |
| TTS | Google Cloud Text-to-Speech |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Deployment | Contabo VPS (Debian), systemd, Nginx, Let's Encrypt |

### Bot (`bot/`)

| Component | Technology |
|-----------|------------|
| Telegram | python-telegram-bot 21 |
| Discord | discord.py 2.3 |
| HTTP client | httpx (async) |
| Runtime | asyncio (both bots run in parallel) |

### Mobile (`mobile/`)

| Component | Technology |
|-----------|------------|
| UI | Vanilla HTML / CSS / JS |
| Android packaging | Capacitor 6 |
| App name | Robo-toutou |

### Tests

pytest + pytest-asyncio, covering the API, auth, API client, and file reader.

---

## Configuration

### API — `api/.env`

```env
# Users (JSON array, bcrypt hashes generated with create_user.py)
USERS='[{"email":"user@example.com","password_hash":"$2b$12$..."}]'

# JWT
JWT_SECRET=a-secret-key-of-at-least-32-characters
JWT_EXPIRE_DAYS=7

# Google Cloud TTS
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
GOOGLE_TTS_LANGUAGE=fr-FR
GOOGLE_TTS_VOICE=fr-FR-Neural2-A
```

**Create a user:**
```bash
cd api && python create_user.py email@example.com mypassword
```

### Bot — `bot/.env`

```env
TELEGRAM_TOKEN=...
DISCORD_TOKEN=...          # optional — Discord is disabled if absent
TTS_API_URL=https://api.yourdomain.com
BOT_EMAIL=bot@example.com
BOT_PASSWORD=password
```

### Mobile — `mobile/src/config.js`

```js
export const API_URL = "https://api.yourdomain.com";
```

---

## Getting started

### Development

```bash
# API
cd api && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Bot
cd bot && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

### Production (systemd)

```bash
sudo systemctl start tts-api
sudo systemctl start tts-bot
```

Service unit files are located at `api/tts-api.service` and `bot/tts-bot.service`.

### Nginx

A sample Nginx configuration with Let's Encrypt is available in `api/nginx.conf.example`.

### Android app

```bash
cd mobile
npm install
npx cap sync
npx cap open android   # opens Android Studio to build the APK
```

---

## API endpoints

| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| `POST` | `/auth/login` | — | Returns a JWT token |
| `POST` | `/tts` | Bearer JWT | Returns an MP3 file |

---

## Tests

```bash
pip install -r api/requirements.txt
pytest
```
