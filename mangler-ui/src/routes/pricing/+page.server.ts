import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async () => {
	// This page is accessible to everyone, no authentication required
	return {};
};