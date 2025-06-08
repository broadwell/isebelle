#!/usr/bin/env python3

"""CLI to load texts from a collection into the db."""

import argparse
import asyncio
import logging
import os
from pathlib import Path

from rich.logging import RichHandler

from isebelle_db import IsebelleDb

# Map lowercase language names to 2+2-letter ISO codes
LANGUAGES = {
    "danish": "da",
    "icelandic": "is",
    "dutch": "nl",
    "german": "de",
    "low german": "nds",
    "flemish": "nld",
}


async def main() -> None:
    """Command-line entry-point."""

    parser = argparse.ArgumentParser(description="Description: {}".format(__doc__))

    parser.add_argument(
        "--drop",
        action="store_true",
        default=False,
        help="Drop (if existing) and recreate tables",
    )

    # Collection metadata that must be supplied:
    # - Collection name (or else inferred from path)
    # - Nationality
    # - Organization
    parser.add_argument("--collection-path", action="store", required=True)
    parser.add_argument("--organization", action="store", required=True)
    parser.add_argument("--country", action="store", required=True)
    parser.add_argument("--search-language", action="store", required=True)
    parser.add_argument("--display-language", action="store", required=True)

    parser.add_argument(
        "--calculate-embeddings",
        action="store_true",
        default=False,
        help="Calculate text embeddings (can also be loaded from a file)",
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=(os.getenv("LOG_LEVEL") or "INFO").upper(),
        format="%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[RichHandler(rich_tracebacks=True)],
    )

    collection_path = Path(args.collection_path)
    assert collection_path.exists(), f"'{collection_path}' does not exist"

    # Currently only support one language and nationality per collection,
    # so sub-colllections, e.g., Verhalenbank Frisian, will need to be loaded
    # separately. But eventually the records may be parsed directly from the
    # XML, allowing more than one language per collection.
    collection_language = args.search_language.lower()
    assert collection_language in LANGUAGES, (
        f"'{collection_language}' language not supported"
    )

    # Create database
    logging.info("Initializing DB...")
    db = await IsebelleDb.create(drop=args.drop)

    collection_name = str(collection_path.name)

    collection_id = await db.add_collection(
        collection_name,
        args.organization,
        args.country,
        args.search_language,
        args.display_language,
    )

    logging.info("Loading story texts into the DB")

    # Load story data into database
    await db.load_stories(
        collection_id,
        collection_name,
        Path(collection_path, "texts"),
        collection_language,
        LANGUAGES[collection_language],
        args.display_language,
        calculate_embeddings=args.calculate_embeddings,
    )

    logging.info("Completed loading story texts into the DB")


if __name__ == "__main__":
    asyncio.run(main())
