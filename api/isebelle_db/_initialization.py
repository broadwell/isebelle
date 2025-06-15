import logging


async def initialize_db(conn, drop=False) -> None:
    if drop:
        logging.warning("Dropping database tables...")
        await conn.execute("DROP TABLE IF EXISTS collection CASCADE;")
        await conn.execute("DROP TABLE IF EXISTS story CASCADE;")

    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS collection (
            id uuid DEFAULT uuid_generate_v1mc() PRIMARY KEY,
            name VARCHAR(150) UNIQUE NOT NULL,
            org_name VARCHAR(150) NOT NULL,
            country VARCHAR(150) NOT NULL,
            search_language VARCHAR(32) NOT NULL,
            display_language VARCHAR(32) NOT NULL,
            story_count INTEGER NOT NULL DEFAULT 0,
            created_on TIMESTAMP NOT NULL DEFAULT NOW()
        )
        ;
        """
    )

    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS story (
            collection_id uuid NOT NULL REFERENCES collection(id),
            collection_name VARCHAR(150) NOT NULL REFERENCES collection(name),
            story_id VARCHAR(150) UNIQUE NOT NULL,
            language_iso_639 VARCHAR(5) NOT NULL,
            text TEXT NOT NULL,
            display_language VARCHAR(32) NOT NULL,
            search_language VARCHAR(32) NOT NULL,
            search_text tsvector,
            text_embedding halfvec(3584) DEFAULT NULL,
            PRIMARY KEY(collection_id, story_id)
        )
        ;
        """
    )

    # Recent embedding models are able to cover a large context window (~8,000 tokens),
    # so chunking probably isn't worth the hassle.
    # await conn.execute(
    #     """
    #     CREATE TABLE IF NOT EXISTS story_chunk (
    #         collection_id uuid NOT NULL REFERENCES collection(id),
    #         collection_name VARCHAR(150) NOT NULL REFERENCES collection(name),
    #         story_id VARCHAR(150) NOT NULL REFERENCES story(story_id),
    #         chunk_seqno INTEGER DEFAULT 1,
    #         text VARCHAR(5000) NOT NULL,
    #         text_embedding vector(16) DEFAULT NULL,
    #         PRIMARY KEY(collection_id, story_id, chunk_seqno)
    #     )
    #     ;
    #     """
    # )


# XXX Maybe shouldn't call this file _initialization if this will be here
async def remove_collection(self, collection_id) -> None:
    async with self._pool.acquire() as conn:
        logging.warning("Removing database entries associated with collection")
        await conn.execute("DELETE FROM collection WHERE id=$1", collection_id)
