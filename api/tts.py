import os
import tempfile
from pathlib import Path

from elevenlabs.client import ElevenLabs
from elevenlabs import save

from utils import strip_markdown

MAX_CHARS = 2500


class TTSError(Exception):
    pass


def generate_tts_audio(text: str) -> bytes:
    """
    Nettoie le texte, appelle ElevenLabs, retourne les bytes mp3.
    Lève TTSError si le texte est trop long ou si l'API échoue.
    """
    text_propre = strip_markdown(text)

    if len(text_propre) > MAX_CHARS:
        raise TTSError(
            f"Le texte dépasse {MAX_CHARS} caractères après nettoyage "
            f"({len(text_propre)} caractères). Veuillez le raccourcir."
        )

    api_key = os.getenv("ELEVENLABS_API_KEY", "")
    voice_id = os.getenv("ELEVENLABS_VOICE_ID", "")

    if not api_key or not voice_id:
        raise TTSError("ELEVENLABS_API_KEY ou ELEVENLABS_VOICE_ID manquant dans .env")

    client = ElevenLabs(api_key=api_key)

    # Génère l'audio en streaming puis sauvegarde dans un fichier temporaire
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        audio = client.generate(
            text=text_propre,
            voice=voice_id,
            model="eleven_multilingual_v2",
        )
        save(audio, tmp_path)
        return Path(tmp_path).read_bytes()
    except Exception as e:
        raise TTSError(f"Erreur ElevenLabs : {e}")
    finally:
        # Suppression du fichier temporaire après lecture
        Path(tmp_path).unlink(missing_ok=True)
