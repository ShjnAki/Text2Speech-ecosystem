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
