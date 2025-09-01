<script>
	import { base } from '$app/paths';
	import { page } from '$app/stores';
	import {
		Content,
		Header,
		SideNav,
		SideNavDivider,
		SideNavItems,
		SideNavLink,
		SkipToContent
	} from 'carbon-components-svelte';
	import Api from 'carbon-icons-svelte/lib/Api.svelte';
	import LogoJupyter from 'carbon-icons-svelte/lib/LogoJupyter.svelte';
	import Home from 'carbon-icons-svelte/lib/Home.svelte';
	import LogoGithub from 'carbon-icons-svelte/lib/LogoGithub.svelte';
	import Search from 'carbon-icons-svelte/lib/Search.svelte';
	import Table from 'carbon-icons-svelte/lib/Table.svelte';
	//import ChartScatter from 'carbon-icons-svelte/lib/ChartScatter.svelte';

	import '@/carbon-theming.css';

	let isSideNavOpen = false;
</script>

<Header
	platformName="Intelligent Search Engine for Belief Legend Embeddings"
	company="ISEBELLE ::"
	bind:isSideNavOpen
>
	<svelte:fragment slot="skip-to-content">
		<SkipToContent />
	</svelte:fragment>
</Header>

<SideNav bind:isOpen={isSideNavOpen} rail>
	<SideNavItems>
		<SideNavLink
			icon={Search}
			text="Search Embeddings"
			href="{base}/search/"
			isSelected={$page.url.pathname == `${base}/search`}
		/>
		<SideNavLink
			icon={Table}
			text="Browse Collections"
			href="{base}/browse/"
			isSelected={$page.url.pathname == `${base}/browse/`}
		/>
		<!-- <SideNavLink
			icon={ChartScatter}
			text="Analytics"
			href="{base}/analytics/"
			isSelected={$page.url.pathname == `${base}/analytics`}
		/> -->
		<SideNavLink
			icon={LogoJupyter}
			text="Notebooks"
			href="/jupyter/tree/notebooks/"
			target="_blank"
			isSelected={$page.url.pathname == `/jupyter/tree/notebooks/`}
		/>
		<SideNavDivider />
		<SideNavLink
			icon={Home}
			text="About"
			href="{base}/"
			isSelected={$page.url.pathname == `${base}/`}
		/>
		<SideNavLink icon={Api} text="API Docs" href="{base}/api/docs" target="_blank" />
		<SideNavLink
			icon={LogoGithub}
			text="GitHub"
			href="https://github.com/broadwell/isebelle"
			target="_blank"
		/>
	</SideNavItems>
</SideNav>

<Content>
	<slot />
</Content>

<style>
	:global(#main-content) {
		height: calc(100vh - 3rem);
		overflow: scroll;
	}
</style>
