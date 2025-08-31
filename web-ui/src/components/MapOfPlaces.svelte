<script>
	import { PUBLIC_API_BASE } from '$env/static/public';
	import { Map, TileLayer, Marker, Popup } from 'sveaflet';
	import { Heat } from 'sveaflet-heat';
	import { MarkerCluster } from 'sveaflet-markercluster';

	/**
	 * @typedef {Object} MapOfPlacesProps
	 * @property {collectionId} UUID || null
	 * @property {storiesList} Array
	 */

	/** @type {MapOfPlacesProps} */
	let { collectionId, storiesList } = $props();

	let placeData = [];
	let latLngs = [];

	const getPlaceData = async () => {
		let response = [];

		if (collectionId !== undefined && collectionId !== '') {
			response = await (await fetch(`${PUBLIC_API_BASE}/collection_places/${collectionId}`)).json();
		} else if (storiesList !== undefined && storiesList.length > 0) {
			const storyIds = storiesList.map((item) => `'${item.id}'`).join(', ');
			response = await (await fetch(`${PUBLIC_API_BASE}/story_places/${storyIds}`)).json();
		}
		placeData = response;
		placeData.forEach((place) => {
			for (let i = 0; i < place['place_stories'].length; i++) {
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
