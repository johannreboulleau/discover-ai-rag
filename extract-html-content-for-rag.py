import trafilatura
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def extraire_texte(html: str) -> str:
    """Extrait le contenu principal d'une page HTML en texte propre."""
    logger.info("Extraction du texte depuis %d caracteres HTML", len(html))
    texte = trafilatura.extract(html) or ""
    logger.info("Texte extrait : %d caracteres", len(texte))
    if not texte:
        logger.warning("L'extraction du texte n'a produit aucun contenu")
    return texte

def extraire_markdown(html: str) -> str:
    """Extrait le contenu principal en Markdown : titres et listes conservés."""
    logger.info("Extraction Markdown depuis %d caracteres en entree", len(html))
    texte = trafilatura.extract(html, output_format="markdown") or ""
    logger.info("Markdown extrait : %d caracteres", len(texte))
    if not texte:
        logger.warning("L'extraction Markdown n'a produit aucun contenu")
    return texte

def extraire_donnees(html: str) -> dict:
    """Extrait le contenu et ses métadonnées (titre, auteur, date)."""
    logger.info("Extraction du contenu et des metadonnees")
    brut = trafilatura.extract(html, output_format="json", with_metadata=True)
    if not brut:
        logger.warning("Aucune donnee extraite du HTML")
        return {}
    donnees = json.loads(brut)
    logger.info(
        "Donnees extraites : titre=%r, auteur=%r, date=%r, texte=%d caracteres",
        donnees.get("title"), donnees.get("author"), donnees.get("date"),
        len(donnees.get("text", "")),
    )
    return {
        "titre": donnees.get("title"),
        "auteur": donnees.get("author"),
        "date": donnees.get("date"),
        "texte": extraire_markdown(html),
    }

def constituer_corpus(urls: list[str]) -> list[dict]:
    """Télécharge et extrait une liste d'URL en documents structurés."""
    corpus = []
    logger.info("Constitution du corpus : %d URL a traiter", len(urls))
    for i, url in enumerate(urls, start=1):
        logger.info("Telechargement [%d/%d] : %s", i, len(urls), url)
        html = trafilatura.fetch_url(url)
        if html is None:
            logger.warning("Telechargement impossible, URL ignoree : %s", url)
            continue
        logger.info("Page telechargee : %d caracteres", len(html))
        donnees = extraire_donnees(html)
        if donnees.get("texte"):
            donnees["source"] = url
            corpus.append(donnees)
            logger.info("Document ajoute au corpus : %s", url)
        else:
            logger.warning("Aucun texte exploitable, URL ignoree : %s", url)
    logger.info("Corpus constitue : %d document(s) sur %d URL", len(corpus), len(urls))
    return corpus

def ecrire_corpus(corpus: list[dict], dossier: str) -> None:
    """Écrit chaque document du corpus dans un fichier JSON."""
    base = Path(dossier)
    logger.info("Ecriture de %d document(s) dans %s", len(corpus), base.resolve())
    if not corpus:
        logger.warning("Le corpus est vide : aucun fichier JSON ne sera ecrit")
    base.mkdir(parents=True, exist_ok=True)
    for i, document in enumerate(corpus):
        fichier = base / f"doc_{i:03d}.json"
        fichier.write_text(
            json.dumps(document, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        logger.info("Fichier ecrit : %s", fichier.resolve())

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    logger.info("Demarrage de l'extraction")
    corpus = constituer_corpus(["https://fr.wikipedia.org/wiki/Boulogne-sur-Mer"])
    ecrire_corpus(corpus, "corpus")
    logger.info("Fin de l'extraction")
