from datetime import datetime
import logging
from pathlib import Path
import re
from io import StringIO
from uuid import UUID

import jsonlines
from lxml import etree
from slugify import slugify

SLUGIFIED_ID_MAX_LENGTH = 64

NS = {
    "datacite": "http://datacite.org/schema/kernel-4",
    "dc": "http://purl.org/dc/elements/1.1/",
    "isebel": "http://www.isebel.eu/ns/isebel",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
}

LANG_CODE_MAPPINGS = {
    "de": ["deu"],
    "da": ["dan"],
    "nl": ["nld"],
    "nn-NO": ["no", "nor"],
    "no": ["nn-NO", "nb-NO"],  # for now
    "fy": ["fry", "frr", "frs"],
}

# This is only needed if the story IDs in the embeddings files don't exactly
# match the story IDs in the DB
collection_prefix = {
    "Evald_Tang_Kristensen": "da.etk.",
    "SAMLA": "no.samla.",
}


def get_value_by_xpath(xml_tree, xpath):
    try:
        return xml_tree.xpath(
            xpath,
            namespaces=NS,
        )[0]
    except IndexError:
        return ""


# Takes an array of potential xpaths, returns the first one that matches,
# or the empty string
def get_value_by_xpaths(xml_tree, xpaths):
    for xpath in xpaths:
        value = get_value_by_xpath(xml_tree, xpath)
        if value != "":
            return value
    return value


STORY_BATCH_SIZE = 100


async def clear_stories(self, collection_id: UUID) -> None:
    await self._pool.execute("DELETE FROM collection WHERE id = $1;", collection_id)


async def add_collection(
    self,
    collection_name: str,
    org_name: str,
    country: str,
    search_language: str,
    display_language: str,
) -> UUID:
    collection_id = await self._pool.fetchval(
        """
        WITH e AS(
            INSERT
                INTO collection (name, org_name, country, search_language, display_language)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT("name") DO NOTHING
                RETURNING id
        )
        SELECT * FROM e
        UNION
            SELECT id FROM collection WHERE name=$1;
        ;
        """,
        collection_name,
        org_name,
        country,
        search_language,
        display_language,
    )

    if not isinstance(collection_id, UUID):
        raise ValueError(f"Unable to create collection '{collection_id}'")

    return collection_id


async def add_place(
    self,
    place_id: str,
    place_name: str,
    lon: float,
    lat: float,
) -> str:
    id = await self._pool.fetchval(
        """
        WITH e AS(
            INSERT
                INTO place (place_id, place_name, lon, lat)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT("place_id") DO NOTHING
                RETURNING place_id
        )
        SELECT * FROM e
        UNION
            SELECT place_id FROM place WHERE place_name=$1;
        ;
        """,
        place_id,
        place_name,
        lon,
        lat,
    )

    return id


async def add_story_place(
    self,
    story_id: str,
    collection_id: UUID,
    place_id: str,
    roles: list,
) -> None:
    await self._pool.execute(
        f"INSERT INTO story_place (story_id, collection_id, place_id, roles) VALUES ($1, $2, $3, $4);",
        story_id,
        collection_id,
        place_id,
        roles,
    )


async def add_story_person(
    self,
    story_id: str,
    collection_id: UUID,
    person_id: str,
    roles: list,
) -> None:
    await self._pool.execute(
        f"INSERT INTO story_person (story_id, collection_id, person_id, roles) VALUES ($1, $2, $3, $4);",
        story_id,
        collection_id,
        person_id,
        roles,
    )


async def add_person(
    self,
    person_id: str,
    person_name: str,
    gender: str,
    profession: str,
) -> str:
    id = await self._pool.fetchval(
        """
        WITH e AS(
            INSERT
                INTO person (person_id, person_name, gender, profession)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT("person_id") DO NOTHING
                RETURNING person_id
        )
        SELECT * FROM e
        UNION
            SELECT person_id FROM person WHERE person_name=$1;
        ;
        """,
        person_id,
        person_name,
        gender,
        profession,
    )

    return id


async def add_keyword(
    self,
    keyword: str,
    language_iso_639: str,
) -> str:
    kwd = await self._pool.fetchval(
        """
        WITH e AS(
            INSERT
                INTO keyword (keyword, language_iso_639)
                VALUES ($1, $2)
                ON CONFLICT("keyword") DO NOTHING
                RETURNING keyword
        )
        SELECT * FROM e
        UNION
            SELECT keyword FROM keyword WHERE keyword=$1;
        ;
        """,
        keyword,
        language_iso_639,
    )

    return kwd


async def load_stories(
    self,
    collection_id: UUID,
    collection_name: str,
    texts_path: Path,
    search_language: str,
    language_code: str,
    display_language: str,
    clear=False,
    reindex=True,
    calculate_embeddings=False,
) -> None:
    if clear:
        logging.debug(f"Clearing stories for collection {collection_id}")
        await self.clear_stories(collection_id)

    logging.info(f"Importing stories from '{texts_path}'...")

    story_files = [p for p in texts_path.glob("*.txt") if p.is_file()]

    logging.info(f"Loading {len(story_files)} files...")

    stories_to_add = []
    texts_to_encode = []

    for s, story_path in enumerate(story_files):
        with open(story_path, "r", encoding="utf-8") as story_file:
            story_text = story_file.read()
        story_id = story_path.name.replace(".txt", "")

        texts_to_encode.append(story_text)

        stories_to_add.append(
            [
                collection_id,
                collection_name,
                story_id,
                language_code,
                story_text,
                search_language,
                display_language,
            ]
        )

        if len(stories_to_add) == STORY_BATCH_SIZE or s == len(story_files) - 1:
            if calculate_embeddings:
                logging.info("Generating embeddings for new batch")
                story_embeddings = self.model.encode(texts_to_encode, batch_size=5)

                for i in range(len(stories_to_add)):
                    stories_to_add[i].append(story_embeddings[i])

                await self._pool.executemany(
                    """
                    INSERT INTO story (
                        collection_id, collection_name, story_id, language_iso_639, text, search_language, display_language, text_embedding)
                        VALUES($1, $2, $3, $4, $5, $6, $7, $8)
                    ;
                    """,
                    stories_to_add,
                )

            else:
                await self._pool.executemany(
                    """
                    INSERT INTO story (
                        collection_id, collection_name, story_id, language_iso_639, text, search_language, display_language)
                        VALUES($1, $2, $3, $4, $5, $6, $7)
                    ;
                    """,
                    stories_to_add,
                )

            logging.info(f"Loaded {len(stories_to_add)} stories")
            stories_to_add = []
            texts_to_encode = []

    await self._pool.execute(
        """
        UPDATE collection
            SET story_count = stories.total_in_collection
            FROM (SELECT count(story_id) as total_in_collection FROM story WHERE collection_id=$1)
                AS stories
            WHERE id=$1
        """,
        collection_id,
    )

    logging.info("Tokenizing story texts for lexical search...")
    await self._pool.execute(
        f"UPDATE story SET search_text = to_tsvector('{search_language}', text) WHERE collection_id = $1;",
        collection_id,
    )

    if reindex:
        logging.info("Creating index for lexical search of all story texts...")
        async with self._pool.acquire() as conn:
            await conn.execute("DROP INDEX IF EXISTS text_search;")
            await conn.execute(
                "CREATE INDEX text_search ON story USING GIN (search_text);"
            )


async def load_stories_xml(
    self,
    collection_id: UUID,
    collection_name: str,
    xml_path: Path,
    search_language: str,
    language_code: str,
    display_language: str,
    clear=False,
    reindex=True,
    calculate_embeddings=False,
) -> None:
    if clear:
        logging.debug(f"Clearing stories for collection {collection_id}")
        await self.clear_stories(collection_id)

    logging.info(f"Importing stories from '{xml_path}'...")

    xml_files = [p for p in xml_path.glob("*.xml") if p.is_file()]

    logging.info(f"Loading {len(xml_files)} files...")

    stories_to_add = []
    texts_to_encode = []

    new_persons = set()
    new_places = set()
    new_keywords = set()

    for s, record_path in enumerate(xml_files):
        file_id = record_path.name.replace(".xml", "")

        # May still need to do this if we're pulling the text out manually
        with open(record_path, "r", encoding="utf-8") as record_file:
            story_xml = record_file.read()

            # Fixes for WossiDia
            story_xml = story_xml.replace(
                "<?xml version='1.0' encoding='UTF-8'?>", ""
            ).replace("<?xml version='1.0' encoding='utf-8'?>", "")
            story_xml = story_xml.replace("xml:", "")
            story_xml = story_xml.replace("<br>", "\n").replace("<br/>", "\n")
            story_xml = re.sub(r"\n+", "\n", story_xml).strip()

            parser = etree.XMLParser(ns_clean=True)
            tree = etree.parse(StringIO(story_xml), parser)

        # XXX Probably should use this as the global story ID, since it includes
        # some collection-specific prefixes and is less likely to collide

        story_id = get_value_by_xpath(tree, "/isebel:story/dc:identifier/text()")

        xml_metadata = get_value_by_xpath(tree, "/isebel:story")

        if "lang" in xml_metadata.attrib:
            xml_lang = xml_metadata.get("lang")
            if (
                xml_lang != language_code
                and xml_lang not in LANG_CODE_MAPPINGS[language_code]
            ):
                logging.warning(
                    f"Story record language {xml_lang} does not match collection language {language_code}"
                )

        # We should get the text from the contents and check whether its language
        # matches what is expected. If not, we should just skip the record.
        story_text_array = []
        text_data = get_value_by_xpath(
            tree, "/isebel:story/isebel:contents/isebel:content"
        )
        if isinstance(text_data, list):
            for text in text_data:
                if (
                    "lang" in text.attrib
                    and text.get("lang") != language_code
                    and text.get("lang") not in LANG_CODE_MAPPINGS[language_code]
                ):
                    logging.warning(
                        f"Text language code {text.get('lang')} does not match story {language_code}, skipping"
                    )
                    continue
                else:
                    story_text_array.append(text.text)
            story_text = " ".join(story_text_array)
        elif isinstance(text_data, str):
            logging.warning(
                f"Story contents element for {story_id} is a string rather than an element, skipping"
            )
            continue
        else:
            if (
                "lang" in text_data.attrib
                and text_data.get("lang") != language_code
                and text_data.get("lang") not in LANG_CODE_MAPPINGS[language_code]
            ):
                logging.warning(
                    f"Text language code {text_data.get('lang')} does not match story {language_code}, skipping"
                )
                continue
            story_text = text_data.text

        if story_text is None or story_text.strip() == "":
            logging.info(f"Story {story_id} contents are empty, skipping")
            continue

        texts_to_encode.append(story_text)

        title_data = get_value_by_xpath(tree, "/isebel:story/dc:title/text()")
        if isinstance(title_data, list):
            for title in title_data:
                if len(title.strip()) > 0:
                    story_title = title
        else:
            story_title = title_data

        story_url = get_value_by_xpath(tree, "/isebel:story/isebel:purl/text()")
        # print("STORY", story_id, story_id, story_title, story_url)

        places = get_value_by_xpath(tree, "/isebel:story/isebel:places")
        for place in places:
            place_name = get_value_by_xpath(place, "dc:title/text()")
            if "id" in place.attrib:
                place_id = f"{collection_name}.{place.get('id')}"
            else:
                place_id = f"{collection_name}.{slugify(place_name)}"[
                    :SLUGIFIED_ID_MAX_LENGTH
                ]
            place_lon = get_value_by_xpath(
                place, "isebel:point/datacite:pointLongitude/text()"
            )
            place_lat = get_value_by_xpath(
                place, "isebel:point/datacite:pointLatitude/text()"
            )
            if (
                place_lon.strip() == ""
                or place_lat.strip() == ""
                or place_lon is None
                or place_lat is None
            ):
                logging.info(f"Place {place_name} has no coordinates, skipping")
                continue

            place_roles = place.xpath("isebel:role/text()", namespaces=NS)
            # print("PLACE", place_id, place_name, place_lon, place_lat, place_roles)

            if place_id not in new_places:
                await add_place(
                    self, place_id, place_name, float(place_lon), float(place_lat)
                )
                new_places.add(place_id)

            await add_story_place(self, story_id, collection_id, place_id, place_roles)

        people = get_value_by_xpath(tree, "/isebel:story/isebel:persons")
        for person in people:
            person_name = get_value_by_xpath(person, "isebel:name/text()")
            if "id" in person.attrib:
                person_id = f"{collection_name}.{person.get('id')}"
            else:
                person_id = f"{collection_name}.{slugify(person_name)}"[
                    :SLUGIFIED_ID_MAX_LENGTH
                ]
            person_roles = person.xpath("isebel:role/text()", namespaces=NS)
            person_gender = get_value_by_xpath(person, "isebel:gender/text()")
            person_profession = get_value_by_xpath(person, "isebel:profession/text()")

            if person_id not in new_persons:
                await add_person(
                    self, person_id, person_name, person_gender, person_profession
                )
                new_persons.add(person_id)

            await add_story_person(
                self, story_id, collection_id, person_id, person_roles
            )

        events = get_value_by_xpath(tree, "/isebel:story/isebel:events")
        story_publication_date = None
        story_collection_date = None
        for event in events:
            event_date = get_value_by_xpath(event, "isebel:date/text()")
            event_role = get_value_by_xpath(event, "isebel:role/text()")
            # Probably only use the event if it's a publication or collection date
            if event_role == "collection":
                story_collection_date = datetime.strptime(event_date, "%Y-%m-%d")
            if event_role == "publication":
                story_publication_date = datetime.strptime(event_date, "%Y-%m-%d")

        keywords = get_value_by_xpath(tree, "/isebel:story/isebel:keywords")
        story_keywords = []
        for keyword in keywords:
            if "lang" in keyword.attrib:
                keyword_lang = keyword.get("lang")
            else:
                keyword_lang = language_code
            keyword_text = keyword.text
            if keyword_text is not None and keyword_text.strip() != "":
                if keyword_text not in new_keywords:
                    await add_keyword(self, keyword_text.strip(), keyword_lang)
                story_keywords.append(keyword_text.strip())

        tale_types = get_value_by_xpath(tree, "/isebel:story/isebel:taleTypes")
        story_tale_types = set()
        for tale_type in tale_types:
            # type_number = None
            # if "number" in tale_type.attrib:
            #     type_number = tale_type.get("number")
            if "title" in tale_type.attrib:
                type_title = tale_type.get("title")
                story_tale_types.add(type_title)

        stories_to_add.append(
            [
                collection_id,
                collection_name,
                story_id,
                story_title,
                language_code,
                story_text,
                search_language,
                display_language,
                story_keywords,
                story_tale_types,
                story_url,
                story_collection_date,
                story_publication_date,
            ]
        )

        if len(stories_to_add) == STORY_BATCH_SIZE or s == len(xml_files) - 1:
            if calculate_embeddings:
                logging.info("Generating embeddings for new batch")
                story_embeddings = self.model.encode(texts_to_encode, batch_size=5)

                for i in range(len(stories_to_add)):
                    stories_to_add[i].append(story_embeddings[i])

                await self._pool.executemany(
                    """
                    INSERT INTO story (
                        collection_id, collection_name, story_id, title, language_iso_639, text, search_language, display_language, keywords, tale_types, story_url, date_collected, date_published, text_embedding)
                        VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
                        ON CONFLICT("story_id") DO NOTHING
                    ;
                    """,
                    stories_to_add,
                )

            else:
                await self._pool.executemany(
                    """
                    INSERT INTO story (
                        collection_id, collection_name, story_id, title, language_iso_639, text, search_language, display_language, keywords, tale_types, story_url, date_collected, date_published)
                        VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                        ON CONFLICT("story_id") DO NOTHING
                    ;
                    """,
                    stories_to_add,
                )

            logging.info(f"Loaded {len(stories_to_add)} stories")
            stories_to_add = []
            texts_to_encode = []

    # Maybe do final steps of setting story count, tokenize text for lexical search
    await self._pool.execute(
        """
        UPDATE collection
            SET story_count = stories.total_in_collection
            FROM (SELECT count(story_id) as total_in_collection FROM story WHERE collection_id=$1)
                AS stories
            WHERE id=$1
        """,
        collection_id,
    )

    logging.info("Tokenizing story texts for lexical search...")
    await self._pool.execute(
        f"UPDATE story SET search_text = to_tsvector('{search_language}', text) WHERE collection_id = $1;",
        collection_id,
    )

    if reindex:
        logging.info("Creating index for lexical search of all story texts...")
        async with self._pool.acquire() as conn:
            await conn.execute("DROP INDEX IF EXISTS text_search;")
            await conn.execute(
                "CREATE INDEX text_search ON story USING GIN (search_text);"
            )


async def load_embeddings(
    self,
    collection_name: str,
    embeddings_path: Path,
    coll_story_ids: list,
    reindex=True,
) -> None:
    logging.info(f"Importing embeddings from '{embeddings_path}'...")

    embeddings_to_add = []

    story_id_prefix = ""
    if collection_name in collection_prefix:
        story_id_prefix = collection_prefix[collection_name]

    print(coll_story_ids)

    with jsonlines.open(embeddings_path) as reader:
        for obj in reader:
            for story_id in obj:

                full_story_id = story_id_prefix + story_id

                if full_story_id not in coll_story_ids:
                    logging.info(
                        f"Couldn't find story ID {full_story_id} from embeddings file in DB, skipping"
                    )
                    continue

                logging.info(f"MATCHED STORY FROM DB {full_story_id} TO EMBEDDINGS FILE")

                embedding = obj[story_id]

                embeddings_to_add.append([full_story_id, embedding])

                if len(embeddings_to_add) == STORY_BATCH_SIZE:
                    await self._pool.executemany(
                        f"""
                        UPDATE story SET text_embedding = $2
                        WHERE story_id = $1 AND collection_name = '{collection_name}'
                        ;
                        """,
                        embeddings_to_add,
                    )

                    embeddings_to_add = []

    if len(embeddings_to_add) > 0:
        await self._pool.executemany(
            f"""
            UPDATE story SET text_embedding = $2
            WHERE story_id = $1 AND collection_name = '{collection_name}'
            ;
            """,
            embeddings_to_add,
        )

    if reindex:
        logging.info("Building embedding search index")
        await self._pool.execute(
            """
            CREATE INDEX ON story
            USING ivfflat (text_embedding halfvec_cosine_ops)
            ;
            """,
        )


async def assign_story_embeddings(self, poem_data, reindex=False) -> None:
    async with self._pool.acquire() as conn:
        await conn.execute(
            "ALTER TABLE pose ADD COLUMN IF NOT EXISTS poem_embedding vector(16) DEFAULT NULL;"
        )
        await conn.executemany(
            """
                UPDATE pose
                SET poem_embedding = $4
                WHERE video_id = $1 AND frame = $2 AND pose_idx = $3
                ;
            """,
            poem_data,
        )

        if reindex:
            logging.info(
                "Creating approximate index for cosine distance of viewpoint-invariant pose embeddings..."
            )
            await conn.execute(
                """
                CREATE INDEX ON pose
                USING ivfflat (poem_embedding vector_cosine_ops)
                ;
                """,
            )

        return
