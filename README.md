# TTS Ecosystem

Système de synthèse vocale (Text-to-Speech) multi-plateforme composé de trois modules indépendants : une API REST, des bots de messagerie et une application mobile Android.

```
┌─────────────┐     JWT      ┌──────────────────────────────┐
│  Mobile     │ ──────────► │                              │
│  (Android)  │             │   API REST (FastAPI)         │
└─────────────┘             │   Google Cloud TTS           │
                             │                              │
┌─────────────┐     JWT      │   VPS Contabo (Debian)       │
│  Bot        │ ──────────► │   systemd + Nginx + HTTPS    │
│  Telegram   │             │                              │
│  Discord    │             └──────────────────────────────┘
└─────────────┘
```

## Fonctionnalités

- **Authentification JWT** — login email/mot de passe, token valide 7 jours
- **Synthèse vocale** — conversion texte → MP3 via Google Cloud TTS (voix neurale française)
- **Bots Telegram & Discord** — acceptent du texte ou des fichiers `.txt`/`.md`, retournent un MP3
- **Application Android** — interface de saisie directe, lecture audio intégrée, limite 5 000 caractères
- **Nettoyage Markdown** — les balises Markdown sont retirées avant la synthèse

---

## Structure du projet

```
tts-ecosystem/
├── api/          # API REST FastAPI
├── bot/          # Bots Telegram + Discord
├── mobile/       # App Android (Capacitor)
└── tests/        # Tests unitaires (pytest)
```

---

## Stack technique

### API (`api/`)

| Composant | Technologie |
|-----------|-------------|
| Framework | FastAPI 0.111 + Uvicorn |
| TTS | Google Cloud Text-to-Speech |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Déploiement | VPS Contabo Debian, systemd, Nginx, Let's Encrypt |

### Bot (`bot/`)

| Composant | Technologie |
|-----------|-------------|
| Telegram | python-telegram-bot 21 |
| Discord | discord.py 2.3 |
| HTTP client | httpx (async) |
| Runtime | asyncio (les deux bots tournent en parallèle) |

### Mobile (`mobile/`)

| Composant | Technologie |
|-----------|-------------|
| Interface | Vanilla HTML / CSS / JS |
| Packaging Android | Capacitor 6 |
| Nom de l'app | Robo-toutou |

### Tests

pytest + pytest-asyncio, couvrant l'API, l'auth, le client API et le lecteur de fichiers.

---

## Configuration

### API — `api/.env`

```env
# Utilisateurs (JSON, hashes bcrypt générés avec create_user.py)
USERS='[{"email":"user@example.com","password_hash":"$2b$12$..."}]'

# JWT
JWT_SECRET=une-clé-secrète-dau-moins-32-caractères
JWT_EXPIRE_DAYS=7

# Google Cloud TTS
GOOGLE_APPLICATION_CREDENTIALS=/chemin/vers/service-account.json
GOOGLE_TTS_LANGUAGE=fr-FR
GOOGLE_TTS_VOICE=fr-FR-Neural2-A
```

**Créer un utilisateur :**
```bash
cd api && python create_user.py email@example.com monmotdepasse
```

### Bot — `bot/.env`

```env
TELEGRAM_TOKEN=...
DISCORD_TOKEN=...          # optionnel — si absent, Discord est désactivé
TTS_API_URL=https://api.mondomaine.com
BOT_EMAIL=bot@example.com
BOT_PASSWORD=motdepasse
```

### Mobile — `mobile/src/config.js`

```js
export const API_URL = "https://api.mondomaine.com";
```

---

## Démarrage

### Dev

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

Les fichiers `.service` sont dans `api/tts-api.service` et `bot/tts-bot.service`.

### Nginx

Un exemple de configuration Nginx avec Let's Encrypt est disponible dans `api/nginx.conf.example`.

### App Android

```bash
cd mobile
npm install
npx cap sync
npx cap open android   # ouvre Android Studio pour builder l'APK
```

---

## Endpoints API

| Méthode | Route | Auth | Description |
|---------|-------|------|-------------|
| `POST` | `/auth/login` | — | Retourne un token JWT |
| `POST` | `/tts` | Bearer JWT | Retourne un fichier MP3 |

---

## Tests

```bash
pip install -r api/requirements.txt
pytest
```
