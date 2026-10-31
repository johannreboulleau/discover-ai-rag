import unicodedata
import re
import json
from pathlib import Path

_BALISES_HTML = re.compile(r"<[^>]+>")

# Zero-width (200b-200f), marques de direction (202a-202e),
# BOM (feff), soft hyphen (00ad).
_INVISIBLES = re.compile(r"[​-‏‪-‮﻿­]")
_ESPACES = re.compile(r"[ \t]+")
_LIGNES_VIDES = re.compile(r"\n\s*\n+")
# Ponctuation forte, suivie d'un espace et d'une majuscule.
_FIN_PHRASE = re.compile(r"(?<=[.!?])\s+(?=[A-ZÀ-ÖØ-Þ])")

def normaliser_espaces(texte: str) -> str:
    """Réduit les espaces multiples et les lignes vides surnuméraires."""
    texte = _ESPACES.sub(" ", texte)
    texte = _LIGNES_VIDES.sub("\n\n", texte)
    lignes = [ligne.strip() for ligne in texte.splitlines()]
    return "\n".join(lignes).strip()

def retirer_html(texte: str) -> str:
    """Supprime les balises HTML résiduelles."""
    return _BALISES_HTML.sub("", texte)

def normaliser_unicode(texte: str) -> str:
    """Ramène le texte à une forme Unicode canonique (NFC)."""
    return unicodedata.normalize("NFC", texte)

def retirer_invisibles(texte: str) -> str:
    """Supprime les caractères invisibles (zero-width, BOM, soft hyphen)."""
    return _INVISIBLES.sub("", texte)

def nettoyer(texte: str) -> str:
    """Pipeline de nettoyage complet, l'ordre des étapes compte."""
    texte = normaliser_unicode(texte)
    texte = retirer_html(texte)
    texte = retirer_invisibles(texte)
    texte = texte.replace("[modifier | modifier le code]", "")
    texte = normaliser_espaces(texte)
    return texte

def segmenter_phrases(texte: str) -> list[str]:
    """Découpe un texte en phrases (segmentation simple par ponctuation)."""
    texte = " ".join(texte.split())
    if not texte:
        return []
    return [p.strip() for p in _FIN_PHRASE.split(texte) if p.strip()]


def ecrire_cleaned_corpus(corpus: list[dict], dossier: str) -> None:
    """Écrit chaque document du corpus dans un fichier JSON."""
    base = Path(dossier)
    base.mkdir(parents=True, exist_ok=True)
    for i, document in enumerate(corpus):
        (base / f"doc_{i:03d}.json").write_text(
            json.dumps(document, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

# if name == "main": permet d’exécuter ce bloc uniquement quand tu lances directement le script :
if __name__ == "__main__":
    fichier = Path(__file__).resolve().parent.parent / "corpus/doc_000.json"
    document = json.loads(fichier.read_text(encoding="utf-8"))
    text = document["texte"]
    text = nettoyer(text)
    # text = segmenter_phrases(text)
    document["texte"] = text
    ecrire_cleaned_corpus([document], "corpus-cleaned")