# ISEBELLE
Intelligent Search Engine for Belief Legend Embeddings

## Installation
1. Clone this repository: `git clone https://github.com/broadwell/isebelle.git` and `cd isebelle`
1. Install and run [Docker](www.docker.com)
1. Install the [just runner](https://github.com/casey/just) for your system
1. Create an appropriate `.env` file in the `isebelle` main folder:
```sh
cat > .env <<EOL
DB_NAME=isebelle
DB_USER=isebelle
DB_PASSWORD=$(LC_ALL=C tr -cd 'a-zA-Z0-9' < /dev/urandom | fold -w24 | head -n 1)
# DB_HOST=localhost    ## Ignored if using docker-compose.yaml
# DB_PORT=5432         ## Ignored if using docker-compose.yaml

STORIES_SRC_FOLDER=/path/to/source/collections

JUPYTER_PASSWORD=secret_password

LOG_LEVEL=INFO       ## Set to DEBUG for additional logging
EOL
```

## Building/running the app and adding new story collections
1. Run `docker compose up` or `just up`
1. If you'll be working with Icelandic texts, be sure to run `just build-icelandic-dictionary` once.
1. Each collection should be a sub-folder of the main data folder identified by `STORIES_SRC_FOLDER` in `.env`. The actual story texts should be in individual .txt files, with the filename providing the story ID, in a folder named `texts/` within the collection folder. Please use underscores (`_`) rather than spaces in the file and folder names. It is recommended that each collection should contain stories in a single language.
1. It can be faster to generate the story sentence embeddings outside of the Docker containers, by running `python api/create_collection_embeddings.py --collection-path [PATH_TO_COLLECTION_FOLDER]`, but in this case you will need to install the script's dependencies on your own.
1. If the story embeddings have been generated as above, you should load the collection's story texts first by running `just add-collection [COLLECTION_NAME] [ORGANIZATION] [COUNTRY] [LANGUAGE]`, then `just add-embeddings [COLLECTION_NAME]`  
If you prefer to generate the story embeddings within the Docker containers while simultaneously importing them along with the story texts, run `just add-collection-and-calculate-embeddings [COLLECTION_NAME] [ORGANIZATION] [COUNTRY] [LANGUAGE]` instead.
1. The search and browse interface for the collections and embeddings should be available at [http://localhost:808/isebelle](http://localhost:8080/isebelle)