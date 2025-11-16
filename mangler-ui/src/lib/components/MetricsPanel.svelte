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
		padding: 2.25rem;
		border-radius: 1.75rem;
		background: radial-gradient(circle at 20% 20%, rgba(44, 217, 142, 0.25), transparent 60%),
			linear-gradient(145deg, rgba(5, 12, 10, 0.95), rgba(10, 25, 20, 0.9));
		border: 1px solid rgba(82, 149, 125, 0.45);
		box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03), 0 25px 50px rgba(0, 0, 0, 0.45);
	}

	.metrics-panel__header {
		display: flex;
		align-items: center;
		gap: 0.6rem;
		font-size: 0.95rem;
		color: rgba(248, 250, 252, 0.8);
		margin-bottom: 2rem;
		text-transform: uppercase;
		letter-spacing: 0.22em;
	}

	.metrics-panel__status-dot {
		width: 0.8rem;
		height: 0.8rem;
		border-radius: 50%;
		background: #45f1a4;
		box-shadow: 0 0 15px rgba(69, 241, 164, 0.7);
		display: inline-flex;
	}

	.metrics-panel__metrics {
		list-style: none;
		padding: 0;
		margin: 0;
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
		gap: 1.1rem;
	}

	.metrics-panel__metrics li {
		padding: 1.2rem;
		border-radius: 1.1rem;
		background: rgba(4, 11, 9, 0.65);
		border: 1px solid rgba(72, 115, 100, 0.45);
	}

	.label {
		font-size: 0.78rem;
		text-transform: uppercase;
		letter-spacing: 0.22em;
		margin-bottom: 0.4rem;
		color: rgba(141, 177, 167, 0.85);
	}

	.value {
		font-size: clamp(1.6rem, 4vw, 2.6rem);
		font-weight: 600;
		margin: 0;
		color: #f4fff9;
	}
</style>
