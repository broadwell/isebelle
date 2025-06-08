from typing import Set
from uuid import UUID

# Lexical search:
# select story_id, text, ts_rank(search_text, query) AS rank FROM story, to_tsquery('danish', 'nis') query WHERE search_text @@ query ORDER by rank DESC LIMIT 1;
# Can also consider using ts_headline() to generate KWIC excerpts


async def lexical_search(
    self, collection_id: UUID, query: str, language: str, limit: int
) -> list:
    return await self._pool.fetch(
        f"""
        SELECT
            story_id,
            collection_name
            search_language,
            display_language,
            text,
            ts_rank(search_text, query) AS rank
        FROM story, to_tsquery('{language}', '{query}') AS query
        WHERE collection_id = $1 AND search_text @@ query
        ORDER BY rank DESC
        LIMIT $2
        """,
        collection_id,
        limit,
    )


async def search_embeddings(
    self,
    text_query: str,
    collections: Set[UUID],
    limit: int = 50,
) -> list:
    # Get embedding of input text
    query_embedding = self.model.encode([text_query], batch_size=1)[0].tolist()

    """Search for nearest texts in the database"""
    distance = f"text_embedding <=> '{query_embedding}'"

    if len(collections) > 1:
        coll_query = f"collection_id IN {tuple(collections)}"
    elif len(collections) == 1:
        coll_item = list(collections)[0]
        if coll_item == "NONE":
            return []
        else:
            coll_query = f"collection_id = UUID('{coll_item}')"
    else:
        coll_query = "TRUE"

    return await self._pool.fetch(
        f"""
        SELECT
            collection_id,
            collection_name,
            story_id,
            text,
            search_language,
            display_language,
            {distance} AS distance
        FROM story
        WHERE {coll_query}
        ORDER BY distance
        LIMIT $1
        """,
        limit,
    )


async def similar_embeddings(
    self,
    story_id: str,
    collection_name: str,
    limit: int = 50,
) -> list:
    # Get embedding of input text

    distance_subquery = f"""
        SELECT text_embedding
        FROM story
        WHERE collection_name = '{collection_name}' AND story_id = '{story_id}'
        """

    """Search for nearest texts in the database"""
    distance = f"text_embedding <=> ({distance_subquery})"

    return await self._pool.fetch(
        f"""
        SELECT
            collection_id,
            collection_name,
            story_id,
            text,
            search_language,
            display_language,
            {distance} AS distance
        FROM story
        ORDER BY distance
        LIMIT $1
        """,
        limit,
    )
