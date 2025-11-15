import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ parent }) => {
	const parentData = await parent();

	// Make sure user is authenticated
	if (!parentData.isAuthenticated) {
		return {
			isAuthenticated: false,
			user: null
		};
	}

	return {
		isAuthenticated: true,
		user: parentData.user
	};
};
