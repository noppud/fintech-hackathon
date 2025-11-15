<script lang="ts">
	type Metrics = {
		available: boolean;
		users24h: number | null;
		sheets24h: number | null;
	};

	export let stats: Metrics | undefined;
	export let className = '';
	export let heading = 'Last 24 hours';
	export let onlineLabel = 'Live telemetry';
	export let offlineLabel = 'Metrics unavailable';
	export let offlineNote = 'Connect Supabase env vars to surface live usage metrics.';

	const metrics = stats ?? {
		available: false,
		users24h: null,
		sheets24h: null
	};
</script>

<div class={`metrics-panel ${className}`.trim()}>
	<div class="metrics-panel__header">
		<span>{heading}</span>
		<span class="metrics-panel__status-dot" aria-hidden="true"></span>
		{#if metrics.available}
			{onlineLabel}
		{:else}
			{offlineLabel}
		{/if}
	</div>

	{#if metrics.available}
		<ul class="metrics-panel__metrics">
			<li>
				<p class="label">Active users</p>
				<p class="value">{metrics.users24h}</p>
			</li>
			<li>
				<p class="label">Sheets mangled</p>
				<p class="value">{metrics.sheets24h}</p>
			</li>
		</ul>
	{:else}
		<p class="metrics-panel__note">{offlineNote}</p>
	{/if}
</div>

<style>
	.metrics-panel {
		padding: 2rem;
		border-radius: 1.5rem;
		background: rgba(15, 23, 42, 0.6);
		border: 1px solid rgba(148, 163, 184, 0.2);
	}

	.metrics-panel__header {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		font-size: 0.95rem;
		color: rgba(248, 250, 252, 0.7);
		margin-bottom: 1.5rem;
	}

	.metrics-panel__status-dot {
		width: 0.75rem;
		height: 0.75rem;
		border-radius: 50%;
		background: #22d3ee;
		box-shadow: 0 0 12px rgba(34, 211, 238, 0.8);
		display: inline-flex;
	}

	.metrics-panel__metrics {
		list-style: none;
		padding: 0;
		margin: 0;
		display: grid;
		gap: 1.25rem;
	}

	.metrics-panel__metrics li {
		padding: 1.1rem;
		border-radius: 1rem;
		background: rgba(2, 6, 23, 0.4);
		border: 1px solid rgba(148, 163, 184, 0.2);
	}

	.metrics-panel__note {
		font-size: 0.95rem;
		color: rgba(248, 250, 252, 0.7);
		margin: 0;
	}

	.label {
		font-size: 0.8rem;
		text-transform: uppercase;
		letter-spacing: 0.2em;
		margin-bottom: 0.35rem;
		color: rgba(148, 163, 184, 0.8);
	}

	.value {
		font-size: clamp(1.5rem, 4vw, 2.5rem);
		font-weight: 600;
		margin: 0;
	}
</style>
