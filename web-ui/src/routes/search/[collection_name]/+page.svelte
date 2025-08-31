<script>
	import MapOfPlaces from '$components/MapOfPlaces.svelte';
	import { DataTable, Link, Pagination, ProgressBar } from 'carbon-components-svelte';
	import Launch from 'carbon-icons-svelte/lib/Launch.svelte';
	import { base } from '$app/paths';
	import { page } from '$app/stores';

	let /** @type {Number} */ currentPage = $state(1);
	let /** @type {Number} */ pageSize = $state(10);
	let /** @type {Number} */ totalMatchingStories = $state(0);
	let /** @type {String} */ collectionName = '';
	let /** @type {String} */ collectionId = '';
	let /** @type {String} */ searchQuery = '';
	let /** @type {StoryRecord[]} */ matchingRows = [];

	const headers = [
		{ key: 'id', value: 'ID' },
		{ key: 'language', value: 'Language' },
		{ key: 'text', value: 'Text' },
		{ key: 'rank', value: 'Search Rank' },
		{ key: 'text_embedding', value: 'Explore' }
	];

	const updatePagination = (/** @type {CustomEvent} */ paginationEvent) => {
		pageSize = paginationEvent.detail.pageSize;
		currentPage = paginationEvent.detail.page;
	};

	const filterRows = (/** @type {StoryRecord[]}*/ storyRows) =>
		storyRows.filter((_, i) => i >= (currentPage - 1) * pageSize && i < currentPage * pageSize);

	const getStoryRows = async () => {
		collectionName = $page.data.collection_name;

		searchQuery = $page.url.searchParams.has('query')
			? $page.url.searchParams.get('query')
			: searchQuery;

		collectionId = await fetch(`${$page.data.apiBase}/collection_id/${collectionName}`).then(
			(data) => data.json().then((data) => data.id)
		);

		const collectionInfo = await fetch(`${$page.data.apiBase}/collection/${collectionId}`).then(
			(data) => data.json()
		);

		const searchLanguage = collectionInfo.search_language;

		matchingRows = await fetch(
			`${$page.data.apiBase}/lexical_search/${collectionName}/${searchQuery}/${searchLanguage}/10000`
		)
			.then((data) => data.json())
			.then((data) =>
				data.map((/** @type {StoryRecord} */ story) => ({
					id: story.story_id,
					text: story.text,
					text_embedding: story.text_embedding,
					language: story.display_language,
					rank: Math.round(story.rank * 1000) / 1000
					//chunks_count: story.chunks.toLocaleString()
				}))
			);

		totalMatchingStories = matchingRows.length;

		return matchingRows;
	};
</script>

{#await getStoryRows()}
	<ProgressBar helperText="Searching for stories..." />
{:then rows}
	<MapOfPlaces storiesList={rows} />
	<Pagination
		totalItems={totalMatchingStories}
		pageSizes={[10, 15, 20]}
		{pageSize}
		page={currentPage}
		on:update={updatePagination}
	/>
	<DataTable
		title={`Matching stories in the collection ${collectionName.replaceAll('_', ' ')}`}
		description="Search text: {searchQuery}"
		zebra
		size="tall"
		{headers}
		rows={filterRows(rows)}
	>
		<svelte:fragment slot="cell" let:row let:cell>
			{#if cell.key === 'text_embedding'}
				<Link
					icon={Launch}
					href={`${base}/similar/${row.id}?collection=${collectionName.replaceAll(' ', '_')}`}
					target="_blank">Similar</Link
				>
			{:else}
				{cell.value}
			{/if}
		</svelte:fragment>
	</DataTable>
{/await}
