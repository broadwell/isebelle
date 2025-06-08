import logging
from pathlib import Path
from uuid import UUID

import jsonlines

STORY_BATCH_SIZE = 100

# async def add_story(self, story_id: str, story_metadata: dict) -> UUID:
#     video_id = await self._pool.fetchval(
#         """
#         INSERT
#             INTO video (video_name, frame_count, fps, width, height)
#             VALUES($1, $2, $3, $4, $5)
#             ON CONFLICT (video_name) DO UPDATE
#             SET frame_count = $2, fps = $3, width = $4, height = $5
#             RETURNING id
#         ;
#         """,
#         story_id,
#         *story_metadata.values(),
#     )

#     if not isinstance(video_id, UUID):
#         raise ValueError(f"Unable to add story '{story_id}'")

#     return video_id


async def clear_stories(self, collection_id: UUID) -> None:
    await self._pool.execute("DELETE FROM collection WHERE id = $1;", collection_id)


async def add_collection(
    self,
    collection_name: str,
    org_name: str,
    country: str,
    search_language: str,
    display_language: str,
) -> UUID:
    collection_id = await self._pool.fetchval(
        """
        INSERT
            INTO collection (name, org_name, country, search_language, display_language)
            VALUES ($1, $2, $3, $4)
            RETURNING id
        ;
        """,
        collection_name,
        org_name,
        country,
        search_language,
        display_language,
    )

    if not isinstance(collection_id, UUID):
        raise ValueError(f"Unable to create collection '{collection_id}'")

    return collection_id


async def load_stories(
    self,
    collection_id: UUID,
    collection_name: str,
    texts_path: Path,
    search_language: str,
    language_code: str,
    display_language: str,
    clear=False,
    reindex=True,
    calculate_embeddings=False,
) -> None:
    if clear:
        logging.debug(f"Clearing stories for collection {collection_id}")
        await self.clear_stories(collection_id)

    logging.info(f"Importing stories from '{texts_path}'...")

    story_files = [p for p in texts_path.glob("*.txt") if p.is_file()]

    logging.info(f"Loading {len(story_files)} files...")

    stories_to_add = []
    texts_to_encode = []

    for s, story_path in enumerate(story_files):
        with open(story_path, "r", encoding="utf-8") as story_file:
            story_text = story_file.read()
        story_id = story_path.name.replace(".txt", "")

        texts_to_encode.append(story_text)

        stories_to_add.append(
            [
                collection_id,
                collection_name,
                story_id,
                language_code,
                story_text,
                search_language,
                display_language,
            ]
        )

        if len(stories_to_add) == STORY_BATCH_SIZE or s == len(story_files) - 1:
            if calculate_embeddings:
                logging.info("Generating embeddings for new batch")
                story_embeddings = self.model.encode(texts_to_encode, batch_size=5)

                for i in range(len(stories_to_add)):
                    stories_to_add[i].append(story_embeddings[i])

                await self._pool.executemany(
                    """
                    INSERT INTO story (
                        collection_id, collection_name, story_id, language_iso_639, text, search_language, display_language, text_embedding)
                        VALUES($1, $2, $3, $4, $5, $6, $7)
                    ;
                    """,
                    stories_to_add,
                )

            else:
                await self._pool.executemany(
                    """
                    INSERT INTO story (
                        collection_id, collection_name, story_id, language_iso_639, text, search_language, display_language)
                        VALUES($1, $2, $3, $4, $5, $6)
                    ;
                    """,
                    stories_to_add,
                )

            logging.info(f"Loaded {len(stories_to_add)} stories")
            stories_to_add = []

    await self._pool.execute(
        """
        UPDATE collection
            SET story_count = stories.total_in_collection
            FROM (SELECT count(story_id) as total_in_collection FROM story WHERE collection_id=$1)
                AS stories
            WHERE id=$1
        """,
        collection_id,
    )

    logging.info("Tokenizing story texts for lexical search...")
    await self._pool.execute(
        f"UPDATE story SET search_text = to_tsvector('{search_language}', text) WHERE collection_id = $1;",
        collection_id,
    )

    if reindex:
        logging.info("Creating index for lexical search of all story texts...")
        async with self._pool.acquire() as conn:
            await conn.execute("DROP INDEX IF EXISTS text_search;")
            await conn.execute(
                "CREATE INDEX text_search ON story USING GIN (search_text);"
            )


async def load_embeddings(
    self,
    collection_name: str,
    embeddings_path: Path,
    reindex=True,
) -> None:
    logging.info(f"Importing embeddings from '{embeddings_path}'...")

    embeddings_to_add = []

    with jsonlines.open(embeddings_path) as reader:
        for obj in reader:
            for story_id in obj:
                embedding = obj[story_id]

                embeddings_to_add.append([story_id, embedding])

                if len(embeddings_to_add) == STORY_BATCH_SIZE:
                    await self._pool.executemany(
                        f"""
                        UPDATE story SET text_embedding = $2
                        WHERE story_id = $1 AND collection_name = '{collection_name}'
                        ;
                        """,
                        embeddings_to_add,
                    )
                    embeddings_to_add = []

    if len(embeddings_to_add) > 0:
        await self._pool.executemany(
            f"""
            UPDATE story SET text_embedding = $2
            WHERE story_id = $1 AND collection_name = '{collection_name}'
            ;
            """,
            embeddings_to_add,
        )

    if reindex:
        logging.info("Building embedding search index")
        await self._pool.execute(
            """
            CREATE INDEX ON story
            USING ivfflat (text_embedding vector_cosine_ops)
            ;
            """,
        )


async def assign_story_embeddings(self, poem_data, reindex=False) -> None:
    async with self._pool.acquire() as conn:
        await conn.execute(
            "ALTER TABLE pose ADD COLUMN IF NOT EXISTS poem_embedding vector(16) DEFAULT NULL;"
        )
        await conn.executemany(
            """
                UPDATE pose
                SET poem_embedding = $4
                WHERE video_id = $1 AND frame = $2 AND pose_idx = $3
                ;
            """,
            poem_data,
        )

        if reindex:
            logging.info(
                "Creating approximate index for cosine distance of viewpoint-invariant pose embeddings..."
            )
            await conn.execute(
                """
                CREATE INDEX ON pose
                USING ivfflat (poem_embedding vector_cosine_ops)
                ;
                """,
            )

        return
