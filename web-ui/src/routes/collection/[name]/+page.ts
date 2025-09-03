import type { PageLoad } from './$types';

export const prerender = 'auto';

export const ssr = false;

export const load: PageLoad = async ({ params }) => {

	return params;

}