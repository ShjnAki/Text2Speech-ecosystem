import os

from google.cloud import texttospeech

from utils import strip_markdown

MAX_CHARS = 5000


class TTSError(Exception):
    pass


def generate_tts_audio(text: str) -> bytes:
    """
    Nettoie le texte, appelle Google Cloud TTS, retourne les bytes mp3.
    Lève TTSError si le texte est trop long ou si l'API échoue.
    """
    text_propre = strip_markdown(text)

    if len(text_propre) > MAX_CHARS:
        raise TTSError(
            f"Le texte dépasse {MAX_CHARS} caractères après nettoyage "
            f"({len(text_propre)} caractères). Veuillez le raccourcir."
        )

    language = os.getenv("GOOGLE_TTS_LANGUAGE", "fr-FR")
    voice_name = os.getenv("GOOGLE_TTS_VOICE", "fr-FR-Neural2-A")

    try:
        client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=text_propre)
        voice = texttospeech.VoiceSelectionParams(
            language_code=language,
            name=voice_name,
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        return response.audio_content
    except Exception as e:
        raise TTSError(f"Erreur Google TTS : {e}")
