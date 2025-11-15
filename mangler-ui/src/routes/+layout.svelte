<script lang="ts">
	import favicon from '$lib/assets/logo-mark-dark.svg';

	let { children, data } = $props();

	const missingKindeConfig = data?.missingKindeConfig;
	const missingEnv = data?.missingEnv ?? [];
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<header class="app-header">
	<div class="app-header__inner">
		<div class="app-header__brand">
			<a href="/">Mangler</a>
		</div>

		{#if data?.isAuthenticated}
			<div class="app-header__user">
				<span class="app-header__email">{data.user?.email}</span>
				<a class="app-header__link" href="/api/auth/logout">Logout</a>
			</div>
		{:else}
			<a class="app-header__link" href="/login">Login</a>
		{/if}
	</div>

	{#if missingKindeConfig}
		<div class="app-banner">
			<span>Authentication not configured.</span>
			<span class="app-banner__vars">Missing: {missingEnv.join(', ')}</span>
		</div>
	{/if}
</header>

<main class="app-main">
	{@render children()}
</main>

<style>
	:global(body) {
		margin: 0;
		background-color: #05070f;
		color: #f8fafc;
		font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
		min-height: 100vh;
	}

	a {
		color: inherit;
	}

	.app-header {
		padding: 1rem 1.5rem 0.5rem;
		background: #05070f;
		position: sticky;
		top: 0;
		z-index: 10;
	}

	.app-header__inner {
		max-width: 1100px;
		margin: 0 auto;
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1rem;
	}

	.app-header__brand a {
		font-weight: 700;
		text-decoration: none;
		color: #f8fafc;
		font-size: 1.1rem;
		letter-spacing: 0.04em;
		text-transform: uppercase;
	}

	.app-header__user {
		display: flex;
		align-items: center;
		gap: 0.85rem;
		font-size: 0.95rem;
		color: #94a3b8;
	}

	.app-header__email {
		color: #cbd5f5;
	}

	.app-header__link {
		text-decoration: none;
		font-weight: 600;
		padding: 0.4rem 0.9rem;
		border-radius: 0.75rem;
		border: 1px solid rgba(148, 163, 184, 0.4);
	}

	.app-header__link:hover {
		border-color: rgba(59, 130, 246, 0.65);
		color: #93c5fd;
	}

	.app-banner {
		margin: 0.75rem auto 0;
		max-width: 1100px;
		padding: 0.65rem 0.9rem;
		border-radius: 0.75rem;
		background-color: rgba(251, 191, 36, 0.08);
		border: 1px solid rgba(251, 191, 36, 0.4);
		display: flex;
		justify-content: space-between;
		align-items: center;
		font-size: 0.85rem;
		color: #fde68a;
		gap: 0.5rem;
	}

	.app-banner__vars {
		color: rgba(254, 243, 199, 0.8);
		font-family: 'JetBrains Mono', 'SFMono-Regular', Consolas, monospace;
		font-size: 0.8rem;
	}

	.app-main {
		padding: 3rem 1.5rem 4rem;
		min-height: calc(100vh - 4rem);
	}

	.app-main :global(section) {
		color: #f8fafc;
	}
</style>
