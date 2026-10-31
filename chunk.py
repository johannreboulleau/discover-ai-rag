import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def chunk_par_sections(markdown):
    """Découpe un Markdown sur ses titres : un chunk par section."""
    sections, titre, corps = [], "(préambule)", []
    for ligne in markdown.splitlines():
        if ligne.lstrip().startswith("#"):
            if any(l.strip() for l in corps):
                sections.append({"titre": titre, "texte": "\n".join(corps).strip()})
            titre, corps = ligne.lstrip("#").strip(), []
        else:
            corps.append(ligne)
    if any(l.strip() for l in corps):
        sections.append({"titre": titre, "texte": "\n".join(corps).strip()})
    return sections


def ecrire_chunks(document: dict, dossier: Path) -> None:
    sections = chunk_par_sections(document["texte"])
    logger.info("Decoupage termine : %d chunk(s)", len(sections))
    if not sections:
        logger.warning("Aucune section exploitable : aucun chunk ne sera ecrit")
    dossier.mkdir(parents=True, exist_ok=True)
    for i, section in enumerate(sections):
        chunk = {
            **document,
            "titre_section": section["titre"],
            "texte": section["texte"],
        }
        fichier = dossier / f"chunk_{i:03d}.json"
        fichier.write_text(
            json.dumps(chunk, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        logger.info("Chunk ecrit : %s", fichier)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    base = Path(__file__).resolve().parent.parent
    fichier = base / "corpus-cleaned" / "doc_000.json"
    logger.info("Lecture du document : %s", fichier)
    document = json.loads(fichier.read_text(encoding="utf-8"))
    ecrire_chunks(document, base / "corpus-chunks")
