import adapter from '@sveltejs/adapter-static';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	kit: {
		// adapter-auto only supports some environments, see https://kit.svelte.dev/docs/adapter-auto for a list.
		// See https://kit.svelte.dev/docs/adapters for more information about adapters.
		adapter: adapter({
			pages: 'build',
			assets: 'build',
			precompress: false,
			strict: true,
			fallback: '404.html'
		}),
		paths: {
			base: '/isebelle'
		},
		alias: {
			'@': './src',
			$components: './src/components'
		},
		prerender: {
			handleHttpError: ({ path, referrer, message }) => {
				if (path === '/jupyter/tree/notebooks/') {
					return;
				}
				console.log("Throwing error, path is", path);
				// otherwise fail the build
				throw new Error(message);
			}
		}
	}
};

export default config;
