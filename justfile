set positional-arguments
set dotenv-load

# [private]
default:
  @just --list

# Start the application
@up:
  docker compose up

# (Re)build all containers
@build:
  docker compose build

# Lint Python files with ruff
@lint:
  docker compose exec -T api ruff check .

# Lint Python files with ruff, and fix where possible
@lint-fix:
  docker compose exec -T api ruff check --fix .

# Build a production bundle of the front-end code for faster UI
@build-prod-ui:
  docker compose exec -T web-ui sh -c 'pnpm $MODULES_DIR/.bin/vite build'

# Drop and rebuild the database (obviously use with caution!)
@drop-and-rebuild-db:
  docker compose exec -T api python -c 'import asyncio;from isebelle_db import IsebelleDb;asyncio.run(IsebelleDb.create(drop=True))'

# Needs to be done once after building the DB container; thanks to https://bjornbr.is/postgres-full-text-search-in-icelandic/
@build-icelandic-dictionary:
  docker cp db-dict-files/icelandic.stop isebelle-db:/usr/share/postgresql/15/tsearch_data
  docker cp db-dict-files/is_is.affix isebelle-db:/usr/share/postgresql/15/tsearch_data
  docker cp db-dict-files/is_is.dict isebelle-db:/usr/share/postgresql/15/tsearch_data
  docker compose exec -T db sh -c 'psql -U isebelle -c "CREATE TEXT SEARCH DICTIONARY icelandic_hunspell (TEMPLATE = ispell, DictFile = is_is, AffFile = is_is, Stopwords = icelandic);"'
  docker compose exec -T db sh -c 'psql -U isebelle -c "CREATE TEXT SEARCH CONFIGURATION public.icelandic ( COPY = pg_catalog.english );"'  
  docker compose exec -T db sh -c 'psql -U isebelle -c "ALTER TEXT SEARCH CONFIGURATION icelandic ALTER MAPPING FOR asciiword, asciihword, hword_asciipart, word, hword, hword_part WITH icelandic_hunspell, simple;"'
  docker compose exec -T db sh -c 'psql -U isebelle -c "ALTER TEXT SEARCH CONFIGURATION icelandic DROP MAPPING FOR email, url, url_path, sfloat, float;"'

# Load all stories in a collection into the DB
@add-collection path organization country search-language display-language:
  docker compose exec -T api sh -c "LOG_LEVEL=$LOG_LEVEL /app/load_collection.py --collection-path \"\$STORIES_SRC_FOLDER/$1\" --organization \"$2\" --country \"$3\" --search-language \"$4\" --display-language \"$5\""

# Load all stories in a collection into the DB and calculate embeddings on the fly during ingest
@add-collection-and-calculate-embeddings path organization country language:
  docker compose exec -T api sh -c "LOG_LEVEL=$LOG_LEVEL /app/load_collection.py --collection-path \"\$STORIES_SRC_FOLDER/$1\" --organization \"$2\" --country \"$3\" --search-language \"$4\" --display-language \"$5\" --calculate-embeddings"

# Load text embeddings from a JSONlines file named like Collection_Name.embeddings.jsonl
# Each line in the file should have the format {story_id: [EMBEDDINGS VECTOR]}
@add-embeddings path:
  docker compose exec -T api sh -c "LOG_LEVEL=$LOG_LEVEL /app/load_embeddings.py --embeddings-path \"\$STORIES_SRC_FOLDER/$1\""

# Refresh PostgreSQL materialized views
# @refresh-db-views:
#   docker compose exec -T db sh -c 'psql -U isebelle -c "REFRESH MATERIALIZED VIEW CONCURRENTLY story_meta;"'

# Load all stories in a collection into the DB, chunking and calculating embeddings
# @add-collection path: && refresh-db-views
#   docker compose exec -T api sh -c "LOG_LEVEL=$LOG_LEVEL /app/load_collection.py --collection-path \"\$STORIES_SRC_FOLDER/$1\""

# Print a mapping of UUIDs to story names
#print-stories:
#  #!/usr/bin/env bash
#  docker exec -i mime-api python - <<< '
#  import asyncio
#  from mime_db import MimeDb
#  async def _():
#      db = await MimeDb.create()
#      print("\n".join(f"""{v.get("id")} {v.get("video_name")}""" for v in await db.get_available_videos()))
#  asyncio.run(_())
#  '
