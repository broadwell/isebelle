<script>
	import MapOfPlaces from '$components/MapOfPlaces.svelte';
	import { DataTable, Link, Pagination, Search, ProgressBar } from 'carbon-components-svelte';
	import Launch from 'carbon-icons-svelte/lib/Launch.svelte';
	import { base } from '$app/paths';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';

	let /** @type {Number} */ currentPage = 1;
	let /** @type {Number} */ pageSize = 10;
	let /** @type {Number} */ totalCollectionStories = 0;
	let /** @type {String} */ collectionName = '';
	let /** @type {String[]} */ collectionIds = [];
	let /** @type {String} */ searchQuery = '';

	const headers = [
		{ key: 'id', value: 'ID' },
		{ key: 'display_language', value: 'Language' },
		{ key: 'text', value: 'Text' },
		{ key: 'text_embedding', value: 'Explore' }
		//{ key: 'chunk_count', value: 'Chunks' }
	];

	const searchTexts = () => {
		goto(`${base}/search/${collectionName}?query=${searchQuery}&limit=10000`);
	};

	const updatePagination = (/** @type {CustomEvent} */ paginationEvent) => {
		let searchParams = $page.url.searchParams;
		if (
			paginationEvent.detail.page != searchParams.get('page') ||
			paginationEvent.detail.pageSize != searchParams.get('pageSize')
		)
			goto(
				`${base}/collection/${collectionName}?page=${paginationEvent.detail.page}&pageSize=${paginationEvent.detail.pageSize}`
			);
	};

	const getStoryRows = async () => {
		collectionName = $page.data.name;

		let searchParams = $page.url.searchParams;

		currentPage = searchParams.has('page') ? searchParams.get('page') : currentPage;
		pageSize = searchParams.has('pageSize') ? searchParams.get('pageSize') : pageSize;

		const collectionId = await fetch(`${$page.data.apiBase}/collection_id/${collectionName}`).then(
			(data) => data.json().then((data) => data.id)
		);
		collectionIds.push(collectionId);

		totalCollectionStories = await fetch(
			`${$page.data.apiBase}/collection_stories_count/${collectionId}`
		).then((data) => data.json().then((data) => data.story_count));

		return await fetch(
			`${$page.data.apiBase}/collection_stories/${collectionId}/${(currentPage - 1) * pageSize}/${pageSize}`
		)
			.then((data) => data.json())
			.then((data) =>
				data.map((/** @type {StoryRecord} */ story) => ({
					id: story.story_id,
					collection_name: story.collection_name,
					display_language: story.display_language,
					text: story.text.trim()
				}))
			);
	};
</script>

{#await getStoryRows()}
	<ProgressBar helperText="Loading..." />
{:then rows}
	<MapOfPlaces {collectionIds} />
	<Pagination
		totalItems={totalCollectionStories}
		pageSizes={[10, 15, 20]}
		page={$page.url.searchParams.has('page')
			? parseInt($page.url.searchParams.get('page'))
			: currentPage}
		pageSize={$page.url.searchParams.has('pageSize')
			? parseInt($page.url.searchParams.get('pageSize'))
			: pageSize}
		on:update={updatePagination}
	/>
	<DataTable
		title={`Stories in the collection ${collectionName}`}
		description="Use the search bar below to run a lexical search on this collection."
		zebra
		size="tall"
		{headers}
		{rows}
	>
		<Search
			bind:value={searchQuery}
			expanded={true}
			on:change={searchTexts}
			placeholder="Enter text to search this collection (original language only)"
		/>
		<svelte:fragment slot="cell" let:row let:cell>
			{#if cell.key === 'text_embedding'}
				<Link
					icon={Launch}
					href={`${base}/similar/${row.id}?collection=${collectionName.replaceAll(' ', '_')}`}
					target="_blank">Similar</Link
				>
			{:else if cell.key === 'text'}
				<div class="cell-text">{cell.value}</div>
			{:else}
				{cell.value}
			{/if}
		</svelte:fragment>
	</DataTable>
{/await}

<style>
	.cell-text {
		white-space: break-spaces;
	}
</style>
