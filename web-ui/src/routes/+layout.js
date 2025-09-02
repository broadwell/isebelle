import { PUBLIC_API_BASE } from '$env/static/public';
const apiBase = PUBLIC_API_BASE;

export const prerender = 'auto';

/** @type {import('./$types').LayoutLoad} */
export function load() {
	return {
		apiBase
	};
}
