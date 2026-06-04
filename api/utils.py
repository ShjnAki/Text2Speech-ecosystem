import re


def strip_markdown(text: str) -> str:
    """Supprime la syntaxe Markdown avant envoi à ElevenLabs."""
    # Blocs de code (``` ... ```)
    text = re.sub(r'```[\s\S]*?```', lambda m: m.group(0).split('\n', 1)[-1].rsplit('\n', 1)[0], text)
    # Titres (#, ##, etc.)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Liens [texte](url) → texte
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    # Gras/italique (**texte**, __texte__, *texte*, _texte_)
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'_(.+?)_', r'\1', text)
    # Code inline (`code`)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    # Listes (- item, * item)
    text = re.sub(r'^[\-\*]\s+', '', text, flags=re.MULTILINE)
    # Nettoyage espaces multiples
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()
