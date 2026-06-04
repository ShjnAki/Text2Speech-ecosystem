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
