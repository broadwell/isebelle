<script>
	import { base } from '$app/paths';
</script>

<svelte:head>
	<title>Isebelle :: Home</title>
	<meta name="description" content="Intelligent Search Engine for BELief Legend Embeddings" />
</svelte:head>

<section>
	<h1>Isebelle: Intelligent Search Engine for BELief Legend Embeddings</h1>
	<div class="logo-row">
		<a href="https://isebel.edu"
			><img src="{base}/static/IsebelLogoMedium.jpg" alt="ISEBEL project logo" /></a
		>
		<a href=""
			><img
				src="{base}/static/comp_foklore_berkeley.png"
				alt="Logo of the UC Berkeley Computational Folklore Lab"
			/></a
		>
		<a href="https://www.verhalenbank.nl/"
			><img src="{base}/static/logo_Meertens.png" alt="Logo of the Meertens Institut" /></a
		>
		<a href="https://www.wossidia.de/"
			><img src="{base}/static/wossidia4isebel.svg" alt="Logo of the Wossidia Archive" /></a
		>
	</div>
	<div class="logo-row">
		<a href="https://ismus.is/tjodfraedi/sagnir/"
			><img src="{base}/static/Sagnagrunnur.png" alt="Logo of the Sagnagrunnur project" /></a
		>
		<a href="https://samla.no/viewer/index/"
			><img src="{base}/static/Samla_black.svg" alt="Logo of the SAMLA project" /></a
		>
	</div>
</section>

<style>
	.logo-row {
		display: flex;
	}
	.logo-row a {
		padding: 10px;
		margin: 10px;
		border: 1px solid black;

		img {
			min-height: 300px;
			max-height: 300px;
			max-width: 500px;
			object-fit: contain;
		}
	}
</style>
