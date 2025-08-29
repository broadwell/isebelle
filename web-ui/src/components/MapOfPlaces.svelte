<script>
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { Loading } from 'carbon-components-svelte';
	import { PUBLIC_API_BASE } from '$env/static/public';

	/**
	 * @typedef {Object} MapOfPlacesProps
	 * @property {collectionId} UUID
	 */

	/** @type {MapOfPlacesProps} */
	let { collectionId } = $props();

	let placeData = [];

	onMount(async () => {
		const response = await (
			await fetch(`${PUBLIC_API_BASE}/collection_places/${collectionId}`)
		).json();
		placeData = response;
		console.log(placeData);
	});
</script>

<div>
	<p>MAP DATA GOES HERE</p>
</div>

<style>
</style>
