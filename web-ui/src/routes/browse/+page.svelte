<script>
	import { DataTable, Search } from 'carbon-components-svelte';
	import { base } from '$app/paths';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';

	let /** @type {string[]} */ selectedRowIds = [];
	let /** @type {String} */ searchQuery = '';

	const headers = [
		{ key: 'name', value: 'Name' },
		{ key: 'org_name', value: 'Organization' },
		{ key: 'country', value: 'Country' },
		{ key: 'language', value: 'Language' },
		{ key: 'story_count', value: 'Stories' }
	];

	const searchEmbeddings = () => {
		goto(`${base}/embeddings/${searchQuery}?collection_ids=${selectedRowIds.join('|')}&limit=1000`);
	};

	const getCollectionRows = async () => {
		return await fetch(`${$page.data.apiBase}/collections/`)
			.then((data) => data.json())
			.then((data) =>
				data.collections.map((/** @type {CollectionRecord} */ collection) => ({
					id: collection.id,
					name: collection.name.replaceAll('_', ' '),
					org_name: collection.org_name,
					country: collection.country,
					language: collection.display_language,
					story_count: collection.story_count.toLocaleString()
				}))
			)
			.then((data) => {
				selectedRowIds = data.map((/** @type {CollectionRecord} */ collection) => collection.id);
				return data;
			});
	};

	const rowClicked = (/** @type {CustomEvent} */ clickEvent) => {
		if (clickEvent.detail.row === undefined) return;
		goto(`${base}/collection/${clickEvent.detail.row.id}`);
	};
</script>

{#await getCollectionRows()}
	<p>Loading...</p>
{:then rows}
	<DataTable
		title="Search and Browse Collections"
		description="Use the search bar below to search multilingual embeddings of all selected collections, or click on a collection to navigate to it for browsing and lexical search."
		batchSelection
		bind:selectedRowIds
		on:click={rowClicked}
		{headers}
		{rows}
	>
		<Search
			bind:value={searchQuery}
			expanded={true}
			on:change={searchEmbeddings}
			placeholder="Search multilingual embeddings of selected collections"
		/>
	</DataTable>
{/await}
