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
	{/if}
</div>

<style>
	.metrics-panel {
		padding: 2rem;
		border-radius: 1.5rem;
		background: rgba(10, 19, 16, 0.85);
		border: 1px solid rgba(75, 104, 93, 0.35);
		box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.02);
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
		background: #45f1a4;
		box-shadow: 0 0 12px rgba(69, 241, 164, 0.7);
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
		background: rgba(5, 12, 10, 0.6);
		border: 1px solid rgba(82, 109, 100, 0.3);
	}

	.label {
		font-size: 0.8rem;
		text-transform: uppercase;
		letter-spacing: 0.2em;
		margin-bottom: 0.35rem;
		color: rgba(129, 157, 148, 0.85);
	}

	.value {
		font-size: clamp(1.5rem, 4vw, 2.5rem);
		font-weight: 600;
		margin: 0;
		color: #f4fff9;
	}
</style>
