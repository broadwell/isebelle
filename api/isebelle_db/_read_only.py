from uuid import UUID


async def get_available_collections(self) -> list:
    return await self._pool.fetch("""SELECT * FROM collection;""")


# async def get_collection_by_id(self, collection_id: UUID) -> asyncpg.Record:
#     return await self._pool.fetchrow(
#         "SELECT * FROM collection WHERE id = $1;", collection_id
#     )


# async def get_collection_by_name(self, collection_name: str) -> asyncpg.Record:
#     return await self._pool.fetchrow(
#         "SELECT * FROM collection WHERE name = $1;", collection_name
#     )


async def get_collection(self, collection_id: UUID) -> str:
    return await self._pool.fetchrow(
        "SELECT * FROM collection WHERE id = $1;", collection_id
    )


async def get_collection_id(self, collection_name: str) -> UUID:
    return await self._pool.fetchrow(
        "SELECT id FROM collection WHERE name = $1;", collection_name
    )


async def get_collection_name(self, collection_id: UUID) -> str:
    return await self._pool.fetchrow(
        "SELECT name FROM collection WHERE id = $1;", collection_id
    )


async def get_collection_stories_count(self, collection_id: UUID) -> int:
    return await self._pool.fetchrow(
        "SELECT story_count FROM collection WHERE id = $1;", collection_id
    )


async def get_collection_stories(
    self, collection_id: UUID, start: int, count: int
) -> list:
    return await self._pool.fetch(
        """SELECT story_id, collection_name, display_language, search_language, text FROM story
            WHERE collection_id = $1 ORDER BY story_id LIMIT $3 OFFSET $2;
        """,
        collection_id,
        start,
        count,
    )
