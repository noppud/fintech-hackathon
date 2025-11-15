<script lang="ts">
	import MetricsPanel from '$lib/components/MetricsPanel.svelte';
	let { data } = $props();

	const userEmail = data?.user?.email;
	const missingKindeConfig = data?.missingKindeConfig;
	const stats = data?.stats;
</script>

<svelte:head>
	<title>Mangler</title>
</svelte:head>

<section class="dashboard">
	<div class="dashboard__hero">
		<p class="dashboard__eyebrow">Operational Console</p>
		<h1>Unified control for Mangler Finance</h1>
		<p class="dashboard__copy">
			Track workflows, automate onboarding and give your team a single secure entry point.
		</p>

		{#if userEmail}
			<div class="dashboard__chip">Signed in as {userEmail}</div>
		{/if}

		<div class="dashboard__actions">
			<a class="dashboard__btn dashboard__btn--primary" href="/extension">Get Extension</a>
			<a class="dashboard__btn dashboard__btn--ghost" href="/api/auth/logout">Sign out</a>
		</div>
	</div>

	<MetricsPanel
		stats={stats}
		className="dashboard__panel"
		offlineNote="Connect Supabase env vars to surface live usage metrics."
	/>

	{#if missingKindeConfig}
		<div class="dashboard__warning">
			<h2>Authentication not configured</h2>
			<p>
				Set the Kinde environment variables described in <code>auth-production-setup.md</code> to enable
				sign-in.
			</p>
		</div>
	{/if}
</section>

<style>
	.dashboard {
		max-width: 1100px;
		margin: 0 auto;
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
		gap: 2rem;
	}

	.dashboard__hero {
		padding: 2.5rem;
		border-radius: 1.5rem;
		background: linear-gradient(135deg, rgba(59, 130, 246, 0.35), rgba(99, 102, 241, 0.25));
		box-shadow: 0 25px 50px rgba(15, 23, 42, 0.55);
	}

	.dashboard__eyebrow {
		font-size: 0.85rem;
		text-transform: uppercase;
		letter-spacing: 0.2em;
		color: rgba(248, 250, 252, 0.8);
		margin-bottom: 0.75rem;
	}

	h1 {
		font-size: clamp(2rem, 4vw, 3rem);
		margin: 0 0 1rem;
	}

	.dashboard__copy {
		color: rgba(248, 250, 252, 0.8);
		margin-bottom: 1.5rem;
		line-height: 1.7;
	}

	.dashboard__chip {
		display: inline-flex;
		padding: 0.5rem 0.85rem;
		border-radius: 999px;
		background: rgba(15, 23, 42, 0.4);
		border: 1px solid rgba(148, 163, 184, 0.4);
		font-size: 0.9rem;
		margin-bottom: 1.2rem;
	}

	.dashboard__actions {
		display: flex;
		flex-wrap: wrap;
		gap: 0.75rem;
	}

	.dashboard__btn {
		border-radius: 0.9rem;
		padding: 0.85rem 1.2rem;
		border: none;
		font-weight: 600;
		cursor: pointer;
		text-decoration: none;
		text-align: center;
		transition: transform 150ms ease, box-shadow 150ms ease;
	}

	.dashboard__btn--primary {
		background: #facc15;
		color: #0f172a;
		box-shadow: 0 10px 20px rgba(250, 204, 21, 0.35);
	}

	.dashboard__btn--ghost {
		background: rgba(15, 23, 42, 0.6);
		color: #f8fafc;
		border: 1px solid rgba(148, 163, 184, 0.5);
	}

	.dashboard__btn:hover {
		transform: translateY(-1px);
	}

	.dashboard__warning {
		grid-column: 1 / -1;
		padding: 1.5rem;
		border-radius: 1rem;
		background: rgba(251, 146, 60, 0.12);
		border: 1px solid rgba(251, 146, 60, 0.4);
		color: #ffedd5;
	}

	.dashboard__warning code {
		font-family: 'JetBrains Mono', 'SFMono-Regular', Consolas, monospace;
		color: #fed7aa;
		font-size: 0.9rem;
	}
</style>
