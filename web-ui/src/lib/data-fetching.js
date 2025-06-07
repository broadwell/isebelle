import { get } from 'svelte/store';
import { page } from '$app/stores';

/**
 * Fetches collection data from the API.
 *
 * @return {Promise<CollectionRecord[]>} A Promise that resolves to the collection data.
 */
export const getCollectionData = async () => {
	const response = await fetch(`${get(page).data.apiBase}/collections/`);
	return await response.json().then((data) => data.collections);
};

/**
 * Fetches text data from the API for a given collection and story ID.
 *
 * @param {string} collectionId - The ID of the collection to fetch.
 * @param {string} storyId - The ID of the story to fetch.
 * @return {Promise<StoryChunkRecord[]>} A Promise that resolves to the story data.
 */
export const getStoryData = async (collectionId, storyId) => {
	const response = await fetch(`${get(page).data.apiBase}/stories/${collectionId}/${storyId}/`);
	return await response.json();
};
