<script>
	import { DataTable, Pagination } from 'carbon-components-svelte';
	import { page } from '$app/stores';

	let /** @type {Number} */ currentPage = $state(1);
	let /** @type {Number} */ pageSize = $state(10);
	let /** @type {Number} */ totalMatchingStories = $state(0);
	let /** @type {String} */ collectionName = $state('');
	let /** @type {String} */ collectionId = '';
	let /** @type {String} */ searchQuery = '';
	let /** @type {StoryRecord[]} */ matchingRows = [];

	const headers = [
		{ key: 'id', value: 'ID' },
		{ key: 'language', value: 'Language' },
		{ key: 'text', value: 'Text' },
		{ key: 'rank', value: 'Search Rank' }
		//{ key: 'chunk_count', value: 'Chunks' }
	];

	const updatePagination = (/** @type {CustomEvent} */ paginationEvent) => {
		pageSize = paginationEvent.detail.pageSize;
		currentPage = paginationEvent.detail.page;
	};

	const filterRows = (/** @type {StoryRecord[]}*/ storyRows) =>
		storyRows.filter((_, i) => i >= (currentPage - 1) * pageSize && i < currentPage * pageSize);

	const getStoryRows = async () => {
		collectionId = $page.data.collection_id;

		searchQuery = $page.url.searchParams.has('query')
			? $page.url.searchParams.get('query')
			: searchQuery;

		const collectionInfo = await fetch(`${$page.data.apiBase}/collection/${collectionId}`).then(
			(data) => data.json()
		);

		collectionName = collectionInfo.name.replaceAll('_', ' ');
		const collectionLanguage = collectionInfo.language;

		matchingRows = await fetch(
			`${$page.data.apiBase}/lexical_search/${collectionId}/${searchQuery}/${collectionLanguage}/10000`
		)
			.then((data) => data.json())
			.then((data) =>
				data.map((/** @type {StoryRecord} */ story) => ({
					id: story.story_id,
					language: story.search_language.replace(/^./, (str) => str.toUpperCase()),
					text: story.text,
					rank: Math.round(story.rank * 1000) / 1000
					//chunks_count: story.chunks.toLocaleString()
				}))
			);

		totalMatchingStories = matchingRows.length;

		return matchingRows;
	};
</script>

{#await getStoryRows()}
	<p>Loading...</p>
{:then rows}
	<Pagination
		totalItems={totalMatchingStories}
		pageSizes={[10, 15, 20]}
		{pageSize}
		page={currentPage}
		on:update={updatePagination}
	/>
	<DataTable
		title={`Matching stories in the collection ${collectionName}`}
		description="Search text: {searchQuery}"
		zebra
		size="tall"
		{headers}
		rows={filterRows(rows)}
	></DataTable>
{/await}
