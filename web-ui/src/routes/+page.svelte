<script>
	import { base } from '$app/paths';
</script>

<svelte:head>
	<title>Isebelle :: Home</title>
	<meta name="description" content="Intelligent Search Engine for BELief Legend Embeddings" />
</svelte:head>

<section>
	<h1>Isebelle: Intelligent Search Engine for BELief Legend Embeddings</h1>

	<p>
		This site is an outgrowth of the <a href="https://isebel.eu"
			>ISEBEL: Intelligent Search Engine for Belief Legends</a
		> project, which uses automatic English cross-translation and an additional set of domain-specific
		key term mappings curated by experts to enable searching and browsing of folklore story collections
		that are recorded a variety of languages. The texts and story, person and place metadata indexed
		for ISEBEL and on this site were generously made available by the institutions below. Click on each
		logo to access the collection at its origin site.
	</p>
	<p>
		The purpose of the Isebelle sub-project is to investigate the use of multilingual semantic
		embeddings to enable further cross-lingual exploration of folklore stories. In addition to
		traditional lexical search of the story texts, this site enables searching for the semantic
		"nearest neighbor" texts of a selected story or of an arbitrary search string, in many
		languages. Please select the "Search" icon in the menu at left to begin exploring the sample
		collections.
	</p>

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
		<a href="https://ismus.is/tjodfraedi/sagnir/"
			><img src="{base}/static/Sagnagrunnur.png" alt="Logo of the Sagnagrunnur project" /></a
		>
		<a href="https://samla.no/viewer/index/"
			><img src="{base}/static/Samla_black.svg" alt="Logo of the SAMLA project" /></a
		>
	</div>
</section>

<style>
	p {
		padding: 20px 0 0 0;
	}
	.logo-row {
		padding: 20px 0 0 0;
		display: flex;
		flex-wrap: wrap;
	}
	.logo-row a {
		padding: 10px;
		margin: 10px;
		border: 1px solid black;

		img {
			min-height: 200px;
			max-height: 200px;
			max-width: 300px;
			object-fit: contain;
		}
	}
</style>
