import json
import logging
import os
from uuid import UUID

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi_utils.timing import add_timing_middleware
from isebelle_db import IsebelleDb

from lib.json_encoder import IsebelleJSONEncoder

load_dotenv()
STORIES_SRC_FOLDER = os.getenv("STORIES_SRC_FOLDER")
CACHE_FOLDER = os.getenv("CACHE_FOLDER")

try:
    assert STORIES_SRC_FOLDER
except AssertionError:
    raise SystemExit("Error: STORIES_SRC_FOLDER is required") from None

try:
    assert CACHE_FOLDER
except AssertionError:
    raise SystemExit("Error: CACHE_FOLDER is required") from None


logging.basicConfig(level=(os.getenv("LOG_LEVEL") or "INFO").upper())
logger = logging.getLogger(__name__)

isebelle_api = FastAPI(root_path=os.environ.get("PUBLIC_API_BASE", "/"))
add_timing_middleware(isebelle_api, record=logger.debug, prefix="api")


isebelle_api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@isebelle_api.on_event("startup")
async def startup():
    isebelle_api.state.db = await IsebelleDb.create(drop=False)


@isebelle_api.get("/")
async def root():
    return {"message": "Isebelle API"}


@isebelle_api.get("/collections/")
async def collections(request: Request):
    available_collections = await request.app.state.db.get_available_collections()
    return {"collections": available_collections}


@isebelle_api.get("/collection/{collection_id}")
async def collection(collection_id: UUID, request: Request):
    collection_name = await request.app.state.db.get_collection(collection_id)
    return collection_name


@isebelle_api.get("/collection_name/{collection_id}")
async def collection_name(collection_id: UUID, request: Request):
    collection_name = await request.app.state.db.get_collection_name(collection_id)
    return collection_name


@isebelle_api.get("/collection_stories_count/{collection_id}")
async def collection_stories_count(collection_id: UUID, request: Request):
    collection_stories_count = await request.app.state.db.get_collection_stories_count(
        collection_id
    )
    return collection_stories_count


@isebelle_api.get("/collection_stories/{collection_id}/{start}/{count}")
async def collection_stories(
    collection_id: UUID, start: int, count: int, request: Request
):
    collection_stories = await request.app.state.db.get_collection_stories(
        collection_id, start, count
    )
    return Response(
        content=json.dumps(collection_stories, cls=IsebelleJSONEncoder),
        media_type="application/json",
    )


@isebelle_api.get("/lexical_search/{collection_id}/{query}/{language}/{limit}")
async def lexical_search(
    collection_id: UUID, query: str, language: str, limit: int, request: Request
):
    matching_stories = await request.app.state.db.lexical_search(
        collection_id, query, language, limit
    )
    return Response(
        content=json.dumps(matching_stories, cls=IsebelleJSONEncoder),
        media_type="application/json",
    )


@isebelle_api.get("/search_embeddings/{query}/{collections}/{limit}")
async def search_embeddings(query: str, collections: str, limit: int, request: Request):
    colls = set(collections.split("|"))
    matching_stories = await request.app.state.db.search_embeddings(query, colls, limit)
    return Response(
        content=json.dumps(matching_stories, cls=IsebelleJSONEncoder),
        media_type="application/json",
    )


@isebelle_api.get("/similar_embeddings/{story_id}/{collection}/{limit}")
async def similar_embeddings(
    story_id: str, collection: str, limit: int, request: Request
):
    matching_stories = await request.app.state.db.similar_embeddings(
        story_id, collection, limit
    )
    return Response(
        content=json.dumps(matching_stories, cls=IsebelleJSONEncoder),
        media_type="application/json",
    )


# @isebelle_api.get("/stories/{collection_id}/")
# async def poses(video_id: UUID, request: Request):
#     frame_data = Path(CACHE_FOLDER, str(video_id), "pose_data_by_frame.json")
#     if frame_data.exists():
#         with frame_data.open("r", encoding="utf-8") as _fh:
#             frame_data = _fh.read()
#     else:
#         frame_data = await request.app.state.db.get_pose_data_by_frame(video_id)
#         frame_data = json.dumps(frame_data, cls=IsebelleJSONEncoder)
#         cache_dir = Path(CACHE_FOLDER, str(video_id))
#         cache_dir.mkdir(parents=True, exist_ok=True)
#         with (cache_dir / "pose_data_by_frame.json").open("w") as _fh:
#             _fh.write(frame_data)

#     return Response(
#         content=frame_data,
#         media_type="application/json",
#     )


if __name__ == "__main__":
    uvicorn.run("server:isebelle_api", host="0.0.0.0", port=5000, reload=True)
