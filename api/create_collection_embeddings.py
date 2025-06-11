#!/usr/bin/env python3

"""CLI to generate embeddings vectors for chunked texts from a collection."""

import argparse

# import asyncio
import logging
import os
from pathlib import Path

import jsonlines
from sentence_transformers import SentenceTransformer

BATCH_SIZE = 5

#model_name = "Alibaba-NLP/gte-multilingual-base"
model_name = "Alibaba-NLP/gte-Qwen2-7B-instruct"
model_slug = model_name.split("/")[-1]

model = SentenceTransformer(model_name, trust_remote_code=True)

# In case you want to reduce the maximum length:
model.max_seq_length = 8192

# from isebelle_db import IsebelleDb
from rich.logging import RichHandler


# async
def main() -> None:
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
    # parser.add_argument("--organization", action="store", required=True)
    # parser.add_argument("--country", action="store", required=True)
    # parser.add_argument("--language", action="store", required=True)

    args = parser.parse_args()

    logging.basicConfig(
        level=(os.getenv("LOG_LEVEL") or "INFO").upper(),
        format="%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[RichHandler(rich_tracebacks=True)],
    )

    collection_path = Path(args.collection_path)
    assert collection_path.exists(), f"'{collection_path}' does not exist"

    # Create database
    # logging.info("Initializing DB...")
    # db = await IsebelleDb.create(drop=args.drop)

    collection_name = str(collection_path.name)
    # collection_id = await db.get_collection_id(collection_name)

    texts_path = Path(collection_path, "texts")
    story_files = [p for p in texts_path.glob("*.txt") if p.is_file()]

    logging.info(f"Loading {len(story_files)} files...")

    outfile = str(
        Path(collection_path, f"{collection_name}.embeddings.{model_slug}.jsonl")
    )

    for story_path in story_files:
        with open(story_path, "r", encoding="utf-8") as story_file:
            story_text = story_file.read()
        story_id = story_path.name.replace(".txt", "")

        story_embedding = model.encode([story_text], batch_size=1)
        with jsonlines.open(outfile, mode="a") as writer:
            writer.write({story_id: story_embedding[0].tolist()})

    # logging.info("Loading story texts into the DB")

    # Load story chunk embedding data into database
    # await db.load_collection_embeddings(
    #     collection_id,
    #     collection_name,
    #     Path(collection_path, "texts"),
    # )

    # logging.info("Completed loading story texts into the DB")


if __name__ == "__main__":
    # asyncio.run(main())
    main()
