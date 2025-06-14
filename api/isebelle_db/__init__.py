"""IsebelleDB class to abstract out the database interaction."""

import logging
import os

import asyncpg
from dotenv import load_dotenv
from pgvector.asyncpg import register_vector
from sentence_transformers import SentenceTransformer

logging.getLogger("dotenv.main").setLevel(logging.FATAL)
load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

try:
    assert all((DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT))
except AssertionError:
    raise SystemExit(
        "Error: DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT are all required"
    ) from None


class IsebelleDb:
    """Class to interact with the database."""

    from isebelle_db._data_loading import (
        add_collection,
        clear_stories,
        load_embeddings,
        load_stories,
    )
    from isebelle_db._initialization import initialize_db, remove_collection
    from isebelle_db._read_only import (
        get_available_collections,
        get_collection,
        get_collection_id,
        get_collection_name,
        get_collection_stories,
        get_collection_stories_count,
    )
    from isebelle_db._text_search import (
        lexical_search,
        search_embeddings,
        similar_embeddings,
    )

    _pool: asyncpg.Pool
    model: None

    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool
        # self.model = SentenceTransformer(
        #     "Alibaba-NLP/gte-multilingual-base",
        #     trust_remote_code=True,
        #     "Alibaba-NLP/gte-Qwen2-7B-instruct",
        #     trust_remote_code=True,
        # )

    @classmethod
    async def create(cls, drop=False) -> "IsebelleDb":
        """Factory method to create a new IsebelleDb instance.
        Used because __init__ doesn't work well with async/await.
        """
        pool = await IsebelleDb.get_pool()

        async with pool.acquire() as conn:
            await IsebelleDb.initialize_db(conn, drop)

        return cls(pool)

    @staticmethod
    async def get_pool() -> asyncpg.Pool:
        pool = await asyncpg.create_pool(
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            host=DB_HOST,
            port=DB_PORT,
            setup=IsebelleDb.setup_connection,
        )
        if not pool:
            raise RuntimeError("Database connection could not be established")
        return pool

    @staticmethod
    async def get_connection() -> asyncpg.Connection:
        conn = await asyncpg.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            host=DB_HOST,
            port=DB_PORT,
        )
        await IsebelleDb.setup_connection(conn)
        return conn

    @staticmethod
    async def setup_connection(conn: asyncpg.Connection):
        await conn.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        await register_vector(conn)
