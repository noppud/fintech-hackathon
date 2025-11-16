<script lang="ts">
	import { page } from '$app/stores';

	let { children, data } = $props();

	const missingKindeConfig = data?.missingKindeConfig;
	const missingEnv = data?.missingEnv ?? [];

	const navLinks = [
		{ href: '/', label: 'Overview' },
		{ href: '/chat', label: 'Sheet Mangler' },
		{ href: '/extension', label: 'Extension' }
	];

	const hideHeaderRoutes = ['/', '/chat', '/extension'];
	const shouldHideHeader = $derived(!data?.isAuthenticated && hideHeaderRoutes.includes($page.url.pathname));
</script>

<svelte:head>
	<link rel="icon" href="/mangler.svg" sizes="any" type="image/svg+xml" />
	<link rel="icon" href="/mangler.png" sizes="32x32" type="image/png" />
</svelte:head>

{#if !shouldHideHeader}
	<header class="app-header">
		<div class="app-header__inner">
			<div class="app-header__brand">
				<a href="/">Mangler</a>
				<p class="app-header__tagline">Operational console</p>
			</div>

			<nav class="app-header__nav" aria-label="Primary">
				{#each navLinks as link}
					<a
						href={link.href}
						class={`app-header__nav-link ${$page.url.pathname === link.href ? 'is-active' : ''}`.trim()}
						aria-current={$page.url.pathname === link.href ? 'page' : undefined}
					>
						{link.label}
					</a>
				{/each}
			</nav>

			{#if data?.isAuthenticated}
				<div class="app-header__user">
					<span class="app-header__email">{data.user?.email}</span>
					<a class="app-header__link" href="/api/auth/logout" data-sveltekit-reload>
						Logout
					</a>
				</div>
			{:else}
				<a class="app-header__link" href="/login">
					Login
				</a>
			{/if}
		</div>

		{#if missingKindeConfig}
			<div class="app-banner">
				<span>Authentication not configured.</span>
				<span class="app-banner__vars">Missing: {missingEnv.join(', ')}</span>
			</div>
		{/if}
	</header>
{/if}

<main class="app-main">
	{@render children()}
</main>

<style>
	:global(*, *::before, *::after) {
		box-sizing: border-box;
	}

	:global(:root) {
		color-scheme: dark;
	}

	:global(body) {
		margin: 0;
		min-height: 100vh;
		font-family: 'Space Grotesk', 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
		background: radial-gradient(circle at top, rgba(64, 217, 133, 0.08), transparent 45%),
			rgb(2, 6, 5);
		color: #effff8;
		line-height: 1.6;
	}

	:global(body)::before {
		content: '';
		position: fixed;
		top: -10%;
		left: 50%;
		width: 60vw;
		height: 60vw;
		background: radial-gradient(circle, rgba(80, 245, 171, 0.15), transparent 60%);
		transform: translateX(-50%);
		z-index: -1;
		filter: blur(20px);
	}

	a {
		color: inherit;
	}

	.app-header {
		padding: 1rem 1.5rem 0.5rem;
		background: rgba(4, 9, 8, 0.85);
		backdrop-filter: blur(18px);
		position: sticky;
		top: 0;
		z-index: 10;
		border-bottom: 1px solid rgba(132, 241, 188, 0.08);
		box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45);
	}

	.app-header__inner {
		max-width: 1200px;
		margin: 0 auto;
		display: grid;
		grid-template-columns: auto 1fr auto;
		align-items: center;
		gap: 1rem;
	}

	.app-header__brand a {
		font-weight: 800;
		text-decoration: none;
		color: #d6ffe9;
		font-size: clamp(1.25rem, 2.5vw, 1.85rem);
		letter-spacing: 0.08em;
		text-transform: uppercase;
	}

	.app-header__tagline {
		margin: 0.1rem 0 0;
		font-size: 0.8rem;
		letter-spacing: 0.28em;
		text-transform: uppercase;
		color: rgba(214, 255, 233, 0.6);
	}

	.app-header__nav {
		display: flex;
		justify-content: center;
		gap: 0.35rem;
		padding: 0.35rem;
		border-radius: 999px;
		border: 1px solid rgba(94, 194, 151, 0.25);
		background: rgba(6, 13, 11, 0.7);
	}

	.app-header__nav-link {
		text-decoration: none;
		font-size: 0.9rem;
		padding: 0.45rem 0.9rem;
		border-radius: 999px;
		color: rgba(219, 255, 239, 0.7);
		transition: color 0.2s ease, background 0.2s ease;
	}

	.app-header__nav-link:hover,
	.app-header__nav-link.is-active {
		color: #04120b;
		background: linear-gradient(135deg, rgba(28, 209, 128, 0.95), rgba(64, 232, 173, 0.9));
	}

	.app-header__user {
		display: flex;
		align-items: center;
		gap: 0.85rem;
		font-size: 0.95rem;
		color: #a1cbc1;
	}

	.app-header__email {
		color: #f3fff9;
		font-weight: 600;
	}

	.app-header__link {
		text-decoration: none;
		font-weight: 700;
		padding: 0.5rem 1.2rem;
		border-radius: 999px;
		border: 1px solid rgba(64, 232, 173, 0.4);
		color: #052016;
		background: linear-gradient(135deg, #4ef0b2, #7afcc7);
		box-shadow: 0 12px 35px rgba(44, 214, 144, 0.25);
		transition: transform 0.2s ease, box-shadow 0.2s ease;
	}

	.app-header__link:hover {
		transform: translateY(-1px);
		box-shadow: 0 18px 35px rgba(64, 232, 173, 0.35);
	}

	.app-banner {
		margin: 0.75rem auto 0;
		max-width: 1200px;
		padding: 0.8rem 1rem;
		border-radius: 1rem;
		background: rgba(255, 171, 102, 0.12);
		border: 1px solid rgba(255, 171, 102, 0.4);
		display: flex;
		justify-content: space-between;
		align-items: center;
		font-size: 0.9rem;
		color: #ffe4c7;
		gap: 0.5rem;
	}

	.app-banner__vars {
		color: rgba(255, 244, 223, 0.9);
		font-family: 'JetBrains Mono', 'SFMono-Regular', Consolas, monospace;
		font-size: 0.8rem;
	}

	.app-main {
		padding: 3.5rem 1.5rem 4.5rem;
		min-height: calc(100vh - 4rem);
	}

	.app-main > :global(*) {
		max-width: 1200px;
		margin: 0 auto;
		width: 100%;
	}

	.app-main :global(section) {
		color: #f8fafc;
	}

	@media (max-width: 900px) {
		.app-header__inner {
			grid-template-columns: 1fr;
			text-align: center;
		}

		.app-header__nav {
			justify-content: center;
		}

		.app-header__user {
			justify-content: center;
		}
	}
</style>
