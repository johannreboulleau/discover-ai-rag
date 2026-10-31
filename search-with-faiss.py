import faiss
import numpy as np
import json
from pathlib import Path
from openai import OpenAI

DIMENSION = 768  # taille des vecteurs de nomic-embed-text

CLIENT = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
MODELE = "nomic-embed-text"

def vectoriser(textes: list[str]) -> np.ndarray:
    """Vectorise des textes ; vecteurs normalisés pour une similarité cosinus."""
    reponse = CLIENT.embeddings.create(model="nomic-embed-text", input=textes)
    vecteurs = np.array([d.embedding for d in reponse.data], dtype="float32")
    faiss.normalize_L2(vecteurs)
    return vecteurs


def rechercher(index, corpus, question, k=3):
    """Renvoie les k documents les plus proches de la question, avec score."""
    scores, indices = index.search(vectoriser([question]), k)
    return [
        {**corpus[i], "similarite": float(score)}
        for score, i in zip(scores[0], indices[0])
        if i != -1
    ]

def main() -> None:

    fichier_index = Path(__file__).resolve().parent.parent / "corpus-indexed/index.json"
    if not fichier_index.is_file():
        raise SystemExit(
            f"Index introuvable : {fichier_index}. Lance d'abord rag/embedding.py."
        )
    corpus = json.loads(fichier_index.read_text(encoding="utf-8"))
    if not corpus:
        raise SystemExit("L'index est vide. Indexe des chunks avant de rechercher.")

    index = faiss.IndexFlatIP(DIMENSION)
    vecteurs = np.array([doc["vecteur"] for doc in corpus], dtype="float32")
    faiss.normalize_L2(vecteurs)
    index.add(vecteurs)

    question = input("Ta question : ").strip()
    if not question:
        raise SystemExit("La question ne doit pas etre vide.")

    resultats = rechercher(index, corpus, question)
    print(f"\nLes {len(resultats)} passages les plus proches :")
    for i, document in enumerate(resultats, start=1):
        print(f"\n--- Resultat {i} ---")
        print(f"Similarite cosinus : {document['similarite']:.4f}")
        print(f"Titre : {document.get('titre', '(sans titre)')}")
        if document.get("titre_section"):
            print(f"Section : {document['titre_section']}")
        if document.get("source"):
            print(f"Source : {document['source']}")
        print(f"\n{document['texte']}")


if __name__ == "__main__":
    main()
