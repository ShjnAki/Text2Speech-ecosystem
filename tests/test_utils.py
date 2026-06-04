import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))

from utils import strip_markdown


def test_supprime_titres():
    assert strip_markdown("# Titre\n## Sous-titre") == "Titre\nSous-titre"


def test_supprime_gras_et_italique():
    assert strip_markdown("**gras** et _italique_") == "gras et italique"


def test_supprime_liens():
    assert strip_markdown("[texte](https://example.com)") == "texte"


def test_supprime_code_inline():
    assert strip_markdown("`code`") == "code"


def test_supprime_blocs_code():
    assert strip_markdown("```python\nprint('hi')\n```") == "print('hi')"


def test_supprime_listes():
    assert strip_markdown("- item1\n* item2") == "item1\nitem2"


def test_texte_sans_markdown_inchange():
    assert strip_markdown("Bonjour le monde") == "Bonjour le monde"


def test_chaine_vide():
    assert strip_markdown("") == ""


def test_supprime_gras_double_underscore():
    assert strip_markdown("__gras__") == "gras"
