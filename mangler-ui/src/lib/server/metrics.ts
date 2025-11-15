import { env } from '$env/dynamic/private';

const SUPABASE_URL = env.SUPABASE_URL;
const SUPABASE_SERVICE_KEY = env.SUPABASE_SERVICE_ROLE_KEY ?? env.SUPABASE_SERVICE_KEY;
const TWENTY_FOUR_HOURS_MS = 24 * 60 * 60 * 1000;

export type Metrics = {
	available: boolean;
	users24h: number | null;
	sheets24h: number | null;
};

async function fetchDistinctCount(
	table: string,
	column: string,
	extraFilters: Record<string, string> = {}
): Promise<number> {
	if (!SUPABASE_URL || !SUPABASE_SERVICE_KEY) {
		throw new Error('Supabase not configured');
	}

	const sinceIso = new Date(Date.now() - TWENTY_FOUR_HOURS_MS).toISOString();
	const params = new URLSearchParams({
		select: column,
		distinct: 'on',
		order: 'created_at.desc',
		created_at: `gte.${sinceIso}`
	});

	for (const [key, value] of Object.entries(extraFilters)) {
		params.set(key, value);
	}

	const response = await fetch(`${SUPABASE_URL.replace(/\/$/, '')}/rest/v1/${table}?${params.toString()}`, {
		method: 'GET',
		headers: {
			apikey: SUPABASE_SERVICE_KEY,
			Authorization: `Bearer ${SUPABASE_SERVICE_KEY}`,
			Accept: 'application/json'
		}
	});

	if (!response.ok) {
		throw new Error(`Supabase request failed: ${response.status}`);
	}

	const payload = await response.json();
	if (!Array.isArray(payload)) {
		throw new Error('Unexpected Supabase payload');
	}

	return payload.length;
}

export async function loadMetrics(): Promise<Metrics> {
	if (!SUPABASE_URL || !SUPABASE_SERVICE_KEY) {
		return { available: false, users24h: null, sheets24h: null };
	}

	try {
		const [users, sheets] = await Promise.all([
			fetchDistinctCount('conversation_messages', 'session_id', { role: 'eq.user' }),
			fetchDistinctCount('cell_value_snapshots', 'spreadsheet_id')
		]);

		return {
			available: true,
			users24h: users,
			sheets24h: sheets
		};
	} catch (error) {
		console.error('Failed to load Supabase metrics', error);
		return { available: false, users24h: null, sheets24h: null };
	}
}
