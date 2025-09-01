import logging


async def initialize_db(conn, drop=False) -> None:
    if drop:
        logging.warning("Dropping database tables...")
        await conn.execute("DROP TABLE IF EXISTS collection CASCADE;")
        await conn.execute("DROP TABLE IF EXISTS story CASCADE;")
        await conn.execute("DROP TABLE IF EXISTS place CASCADE;")
        await conn.execute("DROP TABLE IF EXISTS person CASCADE;")
        await conn.execute("DROP TABLE IF EXISTS keyword CASCADE;")
        await conn.execute("DROP TABLE IF EXISTS story_place CASCADE;")
        await conn.execute("DROP TABLE IF EXISTS story_person CASCADE;")

    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS collection (
            id UUID DEFAULT uuid_generate_v1mc() PRIMARY KEY,
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
            collection_id UUID NOT NULL REFERENCES collection(id),
            collection_name VARCHAR(150) NOT NULL REFERENCES collection(name),
            story_id VARCHAR(150) UNIQUE NOT NULL,
            title VARCHAR(150) DEFAULT NULL,
            language_iso_639 VARCHAR(5) NOT NULL,
            text TEXT NOT NULL,
            display_language VARCHAR(32) NOT NULL,
            search_language VARCHAR(32) NOT NULL,
            search_text tsvector,
            text_embedding halfvec(3584) DEFAULT NULL,
            keywords text[] DEFAULT NULL,
            tale_types text[] DEFAULT NULL,
            story_url VARCHAR(1024) DEFAULT NULL,
            date_collected DATE DEFAULT NULL,
            date_published DATE DEFAULT NULL,
            PRIMARY KEY(collection_id, story_id)
        )
        ;
        """
    )

    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS person (
            person_id VARCHAR(64) UNIQUE NOT NULL,
            person_name VARCHAR(150) NOT NULL,
            gender VARCHAR(16) DEFAULT NULL,
            profession VARCHAR(64) DEFAULT NULL,
            PRIMARY KEY(person_id)
        )
        ;
        """
    )

    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS story_person (
            story_id VARCHAR(150) NOT NULL,
            collection_id UUID NOT NULL,
            person_id VARCHAR(64) NOT NULL,
            roles text[] DEFAULT NULL
        )
        ;
        """
    )

    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS place (
            place_id VARCHAR(64) UNIQUE NOT NULL,
            place_name VARCHAR(150) NOT NULL,
            lon DOUBLE PRECISION NOT NULL,
            lat DOUBLE PRECISION NOT NULL,
            PRIMARY KEY(place_id)
        )
        ;
        """
    )

    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS story_place (
            story_id VARCHAR(150) NOT NULL,
            collection_id UUID NOT NULL,
            place_id VARCHAR(64) NOT NULL,
            roles text[] DEFAULT NULL
        )
        ;
        """
    )

    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS keyword (
            keyword VARCHAR(128) UNIQUE NOT NULL,
            language_iso_639 VARCHAR(5) NOT NULL,
            PRIMARY KEY(keyword)
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
