import json
import logging
from pathlib import Path

import psycopg
from openai import OpenAI
from pgvector.psycopg import register_vector
from psycopg import sql

logger = logging.getLogger(__name__)

DIMENSION = 768   # dimension des vecteurs de nomic-embed-text
DB_NAME = "ragdb"
DSN_ADMIN = "postgresql://postgres:lab@localhost:5435/postgres"
DSN = f"postgresql://postgres:lab@localhost:5435/{DB_NAME}"

CLIENT = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
MODELE = "nomic-embed-text"

def vectoriser(textes: list[str]) -> list[list[float]]:
    """Transforme une liste de textes en vecteurs (embeddings)."""
    reponse = CLIENT.embeddings.create(model=MODELE, input=textes)
    return [d.embedding for d in reponse.data]


def creer_base() -> None:
    """Crée la base de données si elle n'existe pas encore."""
    with psycopg.connect(DSN_ADMIN, autocommit=True) as conn:
        existe = conn.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s", [DB_NAME]
        ).fetchone()
        if not existe:
            conn.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
            logger.info("Base %s creee", DB_NAME)


def connexion() -> psycopg.Connection:
    """Ouvre une connexion PostgreSQL prête pour les vecteurs."""
    conn = psycopg.connect(DSN, autocommit=True)
    conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
    register_vector(conn)            # adapte le type vector côté Python
    return conn


def creer_table(conn: psycopg.Connection) -> None:
    """(Re)crée la table documents et son index HNSW."""
    conn.execute("DROP TABLE IF EXISTS documents")
    conn.execute(
        f"CREATE TABLE documents ("
        f"id serial PRIMARY KEY, titre text, auteur text, date text, "
        f"source text, titre_section text, texte text NOT NULL, "
        f"embedding vector({DIMENSION}))"
    )
    conn.execute(
        "CREATE INDEX ON documents USING hnsw (embedding vector_cosine_ops)"
    )


def charger_chunks(dossier_source: Path) -> list[dict]:
    """Lit les chunks JSON déjà nettoyés."""
    fichiers = sorted(dossier_source.glob("*.json"))
    if not fichiers:
        raise FileNotFoundError(f"Aucun chunk JSON dans {dossier_source}")

    documents = []
    for fichier in fichiers:
        document = json.loads(fichier.read_text(encoding="utf-8"))
        if not isinstance(document.get("texte"), str) or not document["texte"].strip():
            raise ValueError(f"Champ 'texte' absent, vide ou invalide dans {fichier}")
        documents.append(document)
    return documents


def inserer(conn: psycopg.Connection, documents: list[dict]) -> None:
    """Vectorise les chunks et les insère dans la table documents."""
    with conn.transaction(), conn.cursor() as cur:
        for i, doc in enumerate(documents, start=1):
            logger.info("Vectorisation [%d/%d] : %s", i, len(documents), doc.get("titre_section"))
            vecteur = vectoriser([doc["texte"]])[0]
            cur.execute(
                "INSERT INTO documents (titre, auteur, date, source, titre_section, texte, embedding) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s::vector)",
                (
                    doc.get("titre"), doc.get("auteur"), doc.get("date"),
                    doc.get("source"), doc.get("titre_section"), doc["texte"], vecteur,
                ),
            )


def rechercher(conn: psycopg.Connection, question: str, k: int = 3) -> list[dict]:
    """Renvoie les k chunks les plus proches de la question."""
    v_question = vectoriser([question])[0]
    requete = (
        "SELECT titre, titre_section, source, texte, embedding <=> %s::vector AS distance "
        "FROM documents ORDER BY distance LIMIT %s"
    )
    lignes = conn.execute(requete, [v_question, k]).fetchall()
    return [
        {"titre": t, "titre_section": s, "source": src, "texte": txt, "similarite": 1 - d}
        for t, s, src, txt, d in lignes
    ]


def main() -> None:
    base = Path(__file__).resolve().parent
    creer_base()
    with connexion() as conn:
        creer_table(conn)
        documents = charger_chunks(base / "corpus-chunks")
        inserer(conn, documents)
        total = conn.execute("SELECT count(*) FROM documents").fetchone()[0]
        logger.info("Table documents remplie : %d chunks", total)

        question = input("Ta question : ").strip()
        if not question:
            raise SystemExit("La question ne doit pas etre vide.")

        resultats = rechercher(conn, question)
        print(f"\nLes {len(resultats)} passages les plus proches :")
        for i, document in enumerate(resultats, start=1):
            print(f"\n--- Resultat {i} ---")
            print(f"Similarite cosinus : {document['similarite']:.4f}")
            print(f"Titre : {document.get('titre') or '(sans titre)'}")
            if document.get("titre_section"):
                print(f"Section : {document['titre_section']}")
            if document.get("source"):
                print(f"Source : {document['source']}")
            print(f"\n{document['texte']}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    main()
