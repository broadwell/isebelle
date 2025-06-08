/**
 * @typedef {Object} CollectionRecord
 * @property {string} id
 * @property {string} name
 * @property {string} org_name
 * @property {string} country
 * @property {string} search_language
 * @property {string} display_language
 * @property {number} story_count
 * @property {string} created_on
 */

/**
 * @typedef {Object} StoryRecord
 * @property {string} collection_id
 * @property {string} collection_name
 * @property {string} story_id
 * @property {string} language_iso
 * @property {number} total_chunks
 * @property {string} text
 * @property {string} search_language
 * @property {string} display_language
 * @property {string} text_embedding
 * @property {number} rank
 * @property {number} distance
 */

/**
 * @typedef {Object} StoryChunkRecord
 * @property {string} collection_id
 * @property {string} collection_name
 * @property {string} story_id
 * @property {number} chunk_seqno
 * @property {string} text
 */