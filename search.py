import json
import math
from pathlib import Path

if __package__:
    from .embedding import vectoriser
else:
    from embedding import vectoriser

def similarite_cosinus(a: list[float], b: list[float]) -> float:
    """Mesure la proximité de deux vecteurs : 1 identique, 0 sans rapport."""
    produit = sum(x * y for x, y in zip(a, b))
    norme_a = math.sqrt(sum(x * x for x in a))
    norme_b = math.sqrt(sum(y * y for y in b))
    if norme_a == 0 or norme_b == 0:
        return 0.0
    return produit / (norme_a * norme_b)

def rechercher(question: str, corpus: list[dict], k: int = 3) -> list[dict]:
    """Classe les documents du corpus par similarité avec la question."""
    v_question = vectoriser(question)
    classes = sorted(
        [
            {**doc, "similarite": similarite_cosinus(v_question, doc["vecteur"])}
            for doc in corpus
        ],
        key=lambda doc: doc["similarite"],
        reverse=True,
    )
    return classes[:k]


def main() -> None:
    fichier_index = Path(__file__).resolve().parent.parent / "corpus-indexed/index.json"
    if not fichier_index.is_file():
        raise SystemExit(
            f"Index introuvable : {fichier_index}. Lance d'abord rag/embedding.py."
        )
    corpus = json.loads(fichier_index.read_text(encoding="utf-8"))
    if not corpus:
        raise SystemExit("L'index est vide. Indexe des chunks avant de rechercher.")

    question = input("Ta question : ").strip()
    if not question:
        raise SystemExit("La question ne doit pas etre vide.")

    resultats = rechercher(question, corpus)
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
