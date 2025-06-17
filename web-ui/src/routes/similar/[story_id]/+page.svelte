<script>
	import { DataTable, Link, MultiSelect, Pagination, ProgressBar } from 'carbon-components-svelte';
	import Launch from 'carbon-icons-svelte/lib/Launch.svelte';
	import { base } from '$app/paths';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';

	let /** @type {Number} */ currentPage = 1;
	let /** @type {Number} */ pageSize = 10;
	let /** @type {Number} */ totalMatchingStories = 0;
	let /** @type {String} */ storyId = '';
	let /** @type {String} */ storyCollectionName = '';
	let /** @type {StoryRecord[]} */ matchingRows = [];
	let /** @type {string[]} */ selectedCollIds = [];
	let /** @type {string[]} */ allCollIds = [];

	const headers = [
		{ key: 'collection', value: 'Collection' },
		{ key: 'id', value: 'ID' },
		{ key: 'language', value: 'Language' },
		{ key: 'text', value: 'Text' },
		{ key: 'similarity', value: 'Similarity' },
		{ key: 'text_embedding', value: 'Explore' }
	];

	const updateCollections = (/** @type {CustomEvent} */ multiSelectEvent) => {
		if (selectedCollIds.join('|') === multiSelectEvent.detail.selectedIds.join('|')) {
			multiSelectEvent.preventDefault();
		} else if (multiSelectEvent.detail.selectedIds.length === 0) {
			multiSelectEvent.preventDefault();
		} else {
			selectedCollIds = multiSelectEvent.detail.selectedIds;
			const colls = selectedCollIds.join('|');
			goto(`${base}/similar/${storyId}?collection=${storyCollectionName}&collections=${colls}`);
		}
	};

	const getCollectionRows = async () => {
		storyId = $page.data.story_id;

		selectedCollIds = $page.url.searchParams.has('collections')
			? $page.url.searchParams.get('collections').split('|')
			: [];

		return await fetch(`${$page.data.apiBase}/collections/`)
			.then((data) => data.json())
			.then((data) =>
				data.collections.map((/** @type {CollectionRecord} */ collection) => ({
					id: collection.id,
					text: collection.name.replaceAll('_', ' ')
				}))
			)
			.then((data) => {
				allCollIds = data.map((/** @type {CollectionRecord} */ collection) => collection.id);
				return data;
			});
	};

	const updatePagination = (/** @type {CustomEvent} */ paginationEvent) => {
		pageSize = paginationEvent.detail.pageSize;
		currentPage = paginationEvent.detail.page;
	};

	const filterRows = (/** @type {StoryRecord[]}*/ storyRows) =>
		storyRows.filter((_, i) => i >= (currentPage - 1) * pageSize && i < currentPage * pageSize);

	const getStoryRows = async () => {
		let searchParams = $page.url.searchParams;

		storyCollectionName = searchParams.has('collection') ? searchParams.get('collection') : '';

		currentPage = searchParams.has('page') ? searchParams.get('page') : currentPage;
		pageSize = searchParams.has('pageSize') ? searchParams.get('pageSize') : pageSize;

		if (selectedCollIds.length === 0) {
			selectedCollIds = allCollIds;
		}
		const colls = selectedCollIds.length === 0 ? '|' : selectedCollIds.join('|');

		matchingRows = await fetch(
			`${$page.data.apiBase}/similar_embeddings/${storyId}/${storyCollectionName}/${colls}/1000`
		)
			.then((data) => data.json())
			.then((data) =>
				data.map((/** @type {StoryRecord} */ story) => ({
					collection: story.collection_name,
					id: story.story_id,
					language: story.display_language,
					text: story.text,
					similarity: `${Math.round((1 - story.distance) * 10000) / 100}%`,
					embedding: story.text_embedding
				}))
			);

		totalMatchingStories = matchingRows.length;

		return matchingRows;
	};
</script>

{#await getCollectionRows() then colls}
	{#await getStoryRows()}
		<ProgressBar helperText="Searching for similar stories..." />
	{:then rows}
		<div class="control-board">
			<Pagination
				totalItems={totalMatchingStories}
				pageSizes={[10, 15, 20]}
				{pageSize}
				page={currentPage}
				on:update={updatePagination}
			/>
			<MultiSelect
				label="Select collections to search"
				open={true}
				items={colls}
				on:select={updateCollections}
				selectedIds={selectedCollIds}
			/>
		</div>
		<DataTable
			title={'Similar stories in the selected collections'}
			description="Similar to story {storyId} from {storyCollectionName.replaceAll('_', ' ')}"
			zebra
			size="tall"
			{headers}
			rows={filterRows(rows)}
		>
			<svelte:fragment slot="cell" let:row let:cell>
				{#if cell.key === 'text_embedding'}
					<Link
						icon={Launch}
						href={`${base}/similar/${row.id}?collection=${row.collection.replaceAll(' ', '_')}`}
						target="_blank">Similar</Link
					>
				{:else}
					{cell.value}
				{/if}
			</svelte:fragment>
		</DataTable>
		{#if rows.length === 0}
			<p class="no-luck">
				Unable to find any stories that are close semantic matches.<br />You may wish to try
				expanding your query with further terms.<br />Including evocative phrases, nouns, verbs and
				adjectives can be helpful.
			</p>
		{/if}
	{/await}
{/await}

<style>
	.control-board {
		display: flex;
		flex-direction: row;
	}
	.no-luck {
		padding: 10px 0 0 0;
		text-align: center;
		font-weight: bold;
		color: maroon;
	}
</style>
