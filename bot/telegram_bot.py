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
