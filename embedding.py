from openai import OpenAI
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

CLIENT = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
MODELE = "nomic-embed-text"

def vectoriser(texte: str) -> list[float]:
    """Transforme un texte en vecteur (embedding)."""
    reponse = CLIENT.embeddings.create(model=MODELE, input=texte)
    return reponse.data[0].embedding

def indexer(textes: list[str]) -> list[dict]:
    """Vectorise une liste de textes en documents prêts pour la recherche."""
    documents = []
    for i, texte in enumerate(textes, start=1):
        logger.info("Vectorisation [%d/%d] : %d caracteres", i, len(textes), len(texte))
        documents.append({"texte": texte, "vecteur": vectoriser(texte)})
    return documents


def indexer_corpus(dossier_source: Path, dossier_destination: Path) -> None:
    """Lit les chunks et sauvegarde leurs vecteurs avec leurs métadonnées."""
    fichiers = sorted(dossier_source.glob("*.json"))
    if not fichiers:
        raise FileNotFoundError(f"Aucun chunk JSON dans {dossier_source}")

    documents = []
    for fichier in fichiers:
        logger.info("Lecture du chunk : %s", fichier)
        document = json.loads(fichier.read_text(encoding="utf-8"))
        if not isinstance(document.get("texte"), str) or not document["texte"].strip():
            raise ValueError(f"Champ 'texte' absent, vide ou invalide dans {fichier}")
        documents.append(document)

    documents_vectorises = indexer([document["texte"] for document in documents])
    corpus = [
        {**document, **document_vectorise}
        for document, document_vectorise in zip(documents, documents_vectorises)
    ]
    dossier_destination.mkdir(parents=True, exist_ok=True)
    fichier_index = dossier_destination / "index.json"
    fichier_index.write_text(
        json.dumps(corpus, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info("Index sauvegarde : %s (%d chunks)", fichier_index, len(corpus))


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    base = Path(__file__).resolve().parent.parent
    indexer_corpus(base / "corpus-chunks", base / "corpus-indexed")
