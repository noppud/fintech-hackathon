import type { PageServerLoad } from './$types';
import { loadMetrics } from '$lib/server/metrics';

export const load: PageServerLoad = async (event) => {
	const parentData = await event.parent();
	const stats = await loadMetrics();

	return {
		...parentData,
		stats
	};
};
