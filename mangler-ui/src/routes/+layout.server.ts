import { kindeAuthClient, type SessionManager } from '@kinde-oss/kinde-auth-sveltekit';
import { env } from '$env/dynamic/private';
import { dev } from '$app/environment';
import { redirect } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';

const PUBLIC_ROUTES = ['/login'];
const REQUIRED_KINDE_ENV = [
	'KINDE_ISSUER_URL',
	'KINDE_CLIENT_ID',
	'KINDE_CLIENT_SECRET',
	'KINDE_REDIRECT_URL',
	'KINDE_POST_LOGIN_REDIRECT_URL',
	'KINDE_POST_LOGOUT_REDIRECT_URL'
] as const;

export const load: LayoutServerLoad = async ({ request, url }) => {
	const missingEnv = REQUIRED_KINDE_ENV.filter((key) => !env[key]);
	const authConfigured = missingEnv.length === 0;

	let isAuthenticated = false;
	let user = null;

	if (authConfigured) {
		const sessionManager = request as unknown as SessionManager;
		isAuthenticated = await kindeAuthClient.isAuthenticated(sessionManager);

		if (isAuthenticated) {
			user = await kindeAuthClient.getUser(sessionManager);
		}
	}

	if (authConfigured && !isAuthenticated && !PUBLIC_ROUTES.includes(url.pathname)) {
		if (dev) {
			console.info(`[auth] redirecting unauthenticated request for ${url.pathname} -> /login`);
		}
		throw redirect(302, '/login');
	}

	if (authConfigured && isAuthenticated && url.pathname === '/login') {
		if (dev) {
			console.info('[auth] user already signed in; redirecting /login -> /');
		}
		throw redirect(302, '/');
	}

	if (!authConfigured && dev) {
		console.warn(`[auth] missing Kinde env vars: ${missingEnv.join(', ')}`);
	}

	return {
		isAuthenticated,
		user,
		missingKindeConfig: !authConfigured,
		missingEnv
	};
};
