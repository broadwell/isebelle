#!/usr/bin/env python3

"""CLI to load texts from a collection into the db."""

import argparse
import asyncio
import logging
import os
from pathlib import Path

from isebelle_db import IsebelleDb
from rich.logging import RichHandler


async def main() -> None:
    """Command-line entry-point."""

    parser = argparse.ArgumentParser(description="Description: {}".format(__doc__))

    parser.add_argument("--embeddings-path", action="store", required=True)

    args = parser.parse_args()

    logging.basicConfig(
        level=(os.getenv("LOG_LEVEL") or "INFO").upper(),
        format="%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[RichHandler(rich_tracebacks=True)],
    )

    embeddings_path = Path(args.embeddings_path)
    assert embeddings_path.exists(), f"'{embeddings_path}' does not exist"

    # Create database
    logging.info("Initializing DB...")
    db = await IsebelleDb.create()

    embeddings_filename = str(embeddings_path.name)

    collection_name = embeddings_filename.split(".")[0]

    logging.info("Loading collection embeddings into the DB")

    # Load story data into database
    await db.load_embeddings(
        collection_name,
        embeddings_path,
    )

    logging.info("Completed loading collection embeddings into the DB")


if __name__ == "__main__":
    asyncio.run(main())
