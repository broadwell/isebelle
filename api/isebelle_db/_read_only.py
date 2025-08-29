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


async def get_collection_places(self, collection_id: UUID) -> list:
    return await self._pool.fetch(
        """
        WITH collection_stories AS (
            SELECT DISTINCT story_id FROM story WHERE collection_id = $1
        ), collection_places AS (
            SELECT place_id, roles, count(collection_stories.story_id) AS story_count FROM story_place
                LEFT JOIN collection_stories ON story_place.story_id = collection_stories.story_id
                GROUP BY place_id, roles
        )
        SELECT place.place_id, place.place_name, place.lon, place.lat, collection_places.roles, collection_places.story_count
            FROM collection_places, place
            WHERE collection_places.place_id=place.place_id
        ;
        """,
        collection_id,
    )
