-- Spring AI PgVectorStore reads a table "vector_store" (id, content, metadata json, embedding).
-- This view maps the "documents" table filled by pg-vector.py to that format.
CREATE OR REPLACE VIEW vector_store AS
SELECT id::text AS id,
       texte    AS content,
       json_strip_nulls(json_build_object(
           'titre', titre,
           'auteur', auteur,
           'date', date,
           'source', source,
           'titre_section', titre_section
       ))       AS metadata, -- Spring AI rejects null metadata values
       embedding
FROM documents;
