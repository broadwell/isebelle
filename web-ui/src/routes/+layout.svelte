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
	//import DataBase from 'carbon-icons-svelte/lib/DataBase.svelte';
	import LogoJupyter from 'carbon-icons-svelte/lib/LogoJupyter.svelte';
	import Home from 'carbon-icons-svelte/lib/Home.svelte';
	import LogoGithub from 'carbon-icons-svelte/lib/LogoGithub.svelte';
	import Search from 'carbon-icons-svelte/lib/Search.svelte';
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
			icon={Home}
			text="Home"
			href="{base}/"
			isSelected={$page.url.pathname == `${base}/`}
		/>
		<!-- <SideNavLink
			icon={DataBase}
			text="Browse Collections"
			href="{base}/browse/"
			isSelected={$page.url.pathname == `${base}/browse`}
		/> -->
		<SideNavLink
			icon={Search}
			text="Search"
			href="{base}/browse/"
			isSelected={$page.url.pathname == `${base}/browse`}
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
			href="{base}/jupyter/tree/notebooks/"
			isSelected={$page.url.pathname == `${base}/jupyter`}
		/>
		<SideNavDivider />
		<SideNavLink icon={LogoGithub} text="GitHub" href="https://github.com/broadwell/isebelle" />
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
