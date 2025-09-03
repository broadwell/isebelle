from uuid import UUID


async def get_available_collections(self) -> list:
    return await self._pool.fetch("""SELECT * FROM collection;""")


async def get_collections(self) -> list:
    return await self._pool.fetch(
        """
        SELECT
            collection.id,
            name,
            org_name,
            country,
            display_language,
            story_count,
            place_count,
            person_count
        FROM collection
        LEFT JOIN (
            SELECT collection.id, COUNT(*) AS place_count
            FROM collection
            INNER JOIN story_place ON collection.id = story_place.collection_id
            GROUP BY collection.id
        ) AS pl ON collection.id = pl.id
        LEFT JOIN (
            SELECT collection.id, COUNT(*) as person_count
            FROM collection
            INNER JOIN story_person ON collection.id = story_person.collection_id
            GROUP BY collection.id
        ) AS pe ON collection.id = pe.id 
        ORDER BY name
        ;
        """
    )


async def get_collection(self, collection_id: UUID) -> str:
    return await self._pool.fetchrow(
        "SELECT * FROM collection WHERE id = $1;", collection_id
    )


async def get_collection_id(self, collection_name: str) -> str:
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


async def get_collection_story_ids(self, collection_name: str) -> list:
    return await self._pool.fetch(
        """SELECT story_id FROM story
            WHERE collection_name = $1 ORDER BY story_id
        """,
        collection_name,
    )


async def get_collection_places(self, collection_id: UUID) -> list:
    return await self._pool.fetch(
        """
        WITH collection_stories AS (
            SELECT collection_id, story_id FROM story WHERE collection_id = $1
        ), collection_places AS (
            SELECT story_place.place_id, array_agg(DISTINCT collection_stories.story_id) as place_stories FROM story_place
                INNER JOIN collection_stories ON story_place.story_id = collection_stories.story_id
                GROUP BY place_id
        )
        SELECT place.place_id, place.place_name, place.lon, place.lat, collection_places.place_stories
            FROM place INNER JOIN collection_places
            ON collection_places.place_id = place.place_id 
        ;
        """,
        collection_id,
    )


async def get_story_places(self, story_ids: str) -> list:

    return await self._pool.fetch(
        f"""
        WITH place_stories AS (
            SELECT collection_id, story_id FROM story WHERE story_id IN ({story_ids})
        ), story_places AS (
            SELECT story_place.place_id, array_agg(DISTINCT story_place.story_id) as place_stories FROM story_place
                INNER JOIN place_stories ON story_place.story_id = place_stories.story_id
                GROUP BY place_id
        )
        SELECT place.place_id, place.place_name, place.lon, place.lat, story_places.place_stories
            FROM place INNER JOIN story_places
            ON place.place_id = story_places.place_id
        ;
        """
    )
