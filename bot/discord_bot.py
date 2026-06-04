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
