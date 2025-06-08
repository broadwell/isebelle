<script>
	import { DataTable, Link, Pagination } from 'carbon-components-svelte';
	import Launch from 'carbon-icons-svelte/lib/Launch.svelte';
	import { base } from '$app/paths';
	import { page } from '$app/stores';

	let /** @type {Number} */ currentPage = $state(1);
	let /** @type {Number} */ pageSize = $state(10);
	let /** @type {Number} */ totalMatchingStories = $state(0);
	let /** @type {String[]} */ collectionIds = [];
	let /** @type {String} */ searchQuery = '';
	let /** @type {StoryRecord[]} */ matchingRows = [];

	const headers = [
		{ key: 'collection', value: 'Collection' },
		{ key: 'id', value: 'ID' },
		{ key: 'language', value: 'Language' },
		{ key: 'text', value: 'Text' },
		{ key: 'similarity', value: 'Similarity' },
		{ key: 'text_embedding', value: 'Explore' }
		//{ key: 'chunk_count', value: 'Chunks' }
	];

	const updatePagination = (/** @type {CustomEvent} */ paginationEvent) => {
		pageSize = paginationEvent.detail.pageSize;
		currentPage = paginationEvent.detail.page;
	};

	const filterRows = (/** @type {StoryRecord[]}*/ storyRows) =>
		storyRows.filter((_, i) => i >= (currentPage - 1) * pageSize && i < currentPage * pageSize);

	const getStoryRows = async () => {
		searchQuery = $page.data.query;

		collectionIds = $page.url.searchParams.has('collection_ids')
			? $page.url.searchParams.get('collection_ids').split('|')
			: [];

		const colls =
			collectionIds.length === 0 || (collectionIds.length === 1 && collectionIds[0] === '')
				? 'NONE'
				: collectionIds.join('|');

		matchingRows = await fetch(
			`${$page.data.apiBase}/search_embeddings/${searchQuery}/${colls}/1000`
		)
			.then((data) => data.json())
			.then((data) =>
				data.map((/** @type {StoryRecord} */ story) => ({
					collection: story.collection_name,
					id: story.story_id,
					language: story.search_language.replace(/^./, (str) => str.toUpperCase()),
					text: story.text,
					similarity: `${Math.round((1 - story.distance) * 10000) / 100}%`,
					embedding: story.text_embedding
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
		title={'Similar stories in the selected collections'}
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
					href={`${base}/similar/${row.id}?collection=${row.collection}`}
					target="_blank">Similar</Link
				>
			{:else}
				{cell.value}
			{/if}
		</svelte:fragment>
	</DataTable>
{/await}
