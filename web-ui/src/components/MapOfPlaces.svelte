<script>
	import { PUBLIC_API_BASE } from '$env/static/public';
	import { Map, TileLayer, Marker, Popup } from 'sveaflet';
	import { Heat } from 'sveaflet-heat';
	import { MarkerCluster } from 'sveaflet-markercluster';

	/**
	 * @typedef {Object} MapOfPlacesProps
	 * @property {collectionId} UUID
	 */

	/** @type {MapOfPlacesProps} */
	let { collectionId } = $props();

	let placeData = [];
	let latLngs = [];

	const getPlaceData = async () => {
		const response = await (
			await fetch(`${PUBLIC_API_BASE}/collection_places/${collectionId}`)
		).json();
		placeData = response;
		placeData.forEach((place) => {
			for (let i = 0; i < place['story_count']; i++) {
				latLngs.push([place['lat'], place['lon']]);
			}
		});
		return placeData;
	};
</script>

<div style="width:100%; height:500px;">
	<Map
		options={{
			center: [56, 5],
			zoom: 5
		}}
	>
		<TileLayer url={'https://tile.openstreetmap.org/{z}/{x}/{y}.png'} />
		{#await getPlaceData() then placeData}
			<MarkerCluster>
				{#each placeData as place}
					{@const title = String(place['place_name'])}
					<Marker
						latLng={[place['lat'], place['lon']]}
						options={{
							title
						}}
					>
						<Popup options={{ content: title }}></Popup>
					</Marker>
				{/each}
			</MarkerCluster>
			<Heat {latLngs} />
		{/await}
	</Map>
</div>

<style>
</style>
