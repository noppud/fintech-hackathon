import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ url, parent }) => {
	const error = url.searchParams.get('error') ?? null;
	const parentData = await parent();

	if (error && process.env.NODE_ENV !== 'production') {
		console.warn(`[auth] login page error query param detected: ${error}`);
	}

	return {
		error,
		missingKindeConfig: parentData.missingKindeConfig ?? false,
		missingEnv: parentData.missingEnv ?? []
	};
};
