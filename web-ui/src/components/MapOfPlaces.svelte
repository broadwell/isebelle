<script>
	import { PUBLIC_API_BASE } from '$env/static/public';
	import { Map, TileLayer, Marker, Popup } from 'sveaflet';
	import { Heat } from 'sveaflet-heat';
	import { MarkerCluster } from 'sveaflet-markercluster';
	import { mean } from '../lib/utils.js';

	/**
	 * @typedef {Object} MapOfPlacesProps
	 * @property {collectionIds} UUID[] || null
	 * @property {storiesList} Array
	 */

	/** @type {MapOfPlacesProps} */
	let { collectionIds, storiesList } = $props();

	let placeData = [];
	let latLngs = [];

	let /** @type Map */ map = $state();

	let avgLat = 56;
	let avgLon = 5;

	const getPlaceData = async () => {
		if (collectionIds !== undefined && collectionIds.length > 0) {
			const collectionIdStrings = collectionIds.map((item) => `'${item}'`).join(', ');
			placeData = await (
				await fetch(`${PUBLIC_API_BASE}/collection_places/${collectionIdStrings}`)
			).json();
		} else if (storiesList !== undefined && storiesList.length > 0) {
			//const storyIds = storiesList.map((item) => `'${item.id}'`).join(', ');
			const storyIds = storiesList.map((item) => item.id);
			// Need to split the list into multiple requests to avoid HTTP 414 (URI too long) errors
			let theseStoryIds = [];
			let queryStoryIds = '';
			let response = null;
			for (let i = 0; i < storyIds.length; i++) {
				theseStoryIds.push(storyIds[i]);
				queryStoryIds = theseStoryIds.map((item) => `'${item}'`).join(', ');
				if (queryStoryIds.length > 1800 || i === storyIds.length - 1) {
					response = await (await fetch(`${PUBLIC_API_BASE}/story_places/${queryStoryIds}`)).json();
					placeData = placeData.concat(response);
					theseStoryIds = [];
				}
			}
		}
		let /** @type [Number] | [] */ allLats = [];
		let /** @type [Number] | [] */ allLons = [];
		placeData.forEach((place) => {
			for (let i = 0; i < place['place_stories'].length; i++) {
				latLngs.push([place['lat'], place['lon']]);
				allLats.push(place['lat']);
				allLons.push(place['lon']);
			}
		});
		avgLat = mean(allLats) || avgLat;
		avgLon = mean(allLons) || avgLon;
		if (map !== undefined) map.setView([avgLat, avgLon], 5, { duration: 1, animate: true });

		return placeData;
	};
</script>

<div style="width:100%; height:500px;">
	<Map bind:instance={map} options={{ center: [56, 5], zoom: 5 }}>
		<TileLayer url={'https://tile.openstreetmap.org/{z}/{x}/{y}.png'} />
		{#await getPlaceData() then placeData}
			<MarkerCluster>
				{#each placeData as place}
					{@const name = String(place['place_name'])}
					{@const stories = place['place_stories'].join('<br>')}
					<Marker
						latLng={[place['lat'], place['lon']]}
						options={{
							name
						}}
					>
						<Popup
							options={{
								content: `<div style="max-height: 300px; overflow-y: scroll"><strong>${name}</strong><br>${stories}</dev>`
							}}
						></Popup>
					</Marker>
				{/each}
			</MarkerCluster>
			<Heat
				{latLngs}
				options={{
					gradient: {
						0.1: 'pink',
						0.65: 'orange',
						1: 'purple'
					}
				}}
			/>
		{/await}
	</Map>
</div>

<style>
</style>
