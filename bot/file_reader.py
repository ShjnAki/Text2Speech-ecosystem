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
