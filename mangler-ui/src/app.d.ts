// See https://svelte.dev/docs/kit/types#app.d.ts
// for information about these interfaces
declare global {
	namespace App {
		// interface Error {}
		// interface Locals {}
		// interface PageData {}
		// interface PageState {}
		// interface Platform {}
	}

	interface Window {
		google?: {
			accounts?: {
				oauth2?: {
					initTokenClient: (config: {
						client_id: string;
						scope: string;
						callback: (response: { access_token?: string; expires_in?: number }) => void;
						error_callback?: (error: { error?: string; error_description?: string }) => void;
					}) => {
						requestAccessToken: (options?: { prompt?: string }) => void;
					};
				};
			};
		};
	}
}

export {};
