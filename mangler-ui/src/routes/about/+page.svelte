<script lang="ts">
	const features = [
		{
			title: 'Formula Validation',
			description: 'Automatically detect and fix formula errors across your entire spreadsheet ecosystem.',
			icon: '✓'
		},
		{
			title: 'Data Integrity',
			description: 'Cross-reference checking to ensure data consistency across multiple sheets and workbooks.',
			icon: '🔍'
		},
		{
			title: 'Privacy Scanning',
			description: 'Detect personally identifiable information and sensitive data with advanced pattern recognition.',
			icon: '🔒'
		},
		{
			title: 'AI-Powered Analysis',
			description: 'Leverage advanced machine learning to identify anomalies and suggest optimizations.',
			icon: '🤖'
		},
		{
			title: 'Real-time Monitoring',
			description: 'Continuous monitoring of your spreadsheets with instant alerts for critical issues.',
			icon: '📊'
		},
		{
			title: 'Workflow Automation',
			description: 'Build multi-step workflows that span across Google Sheets, Gmail, and Drive.',
			icon: '⚡'
		}
	];

	const stats = [
		{ value: '10,000+', label: 'Sheets analyzed' },
		{ value: '99.9%', label: 'Uptime' },
		{ value: '<100ms', label: 'Response time' },
		{ value: '24/7', label: 'Monitoring' }
	];
</script>

<svelte:head>
	<title>About | Mangler</title>
</svelte:head>

<section class="about">
	<div class="about__hero">
		<div class="about__hero-content">
			<div class="about__eyebrow-row">
				<p class="about__eyebrow">About Mangler</p>
				<span class="about__badge">Open Source</span>
			</div>
			<h1>Your intelligent spreadsheet guardian</h1>
			<p class="about__hero-text">
				Mangler is an AI-powered operational console that keeps your Google Sheets honest. It continuously monitors, validates, and optimizes your spreadsheets so your team can focus on making decisions, not debugging formulas.
			</p>
			<div class="about__actions">
				<a class="about__btn about__btn--primary" href="/login">Get started</a>
				<a class="about__btn about__btn--secondary" href="https://github.com/noppud/mangler.finance" target="_blank" rel="noopener noreferrer">
					<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
						<path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
					</svg>
					View on GitHub
				</a>
				<a class="about__btn about__btn--ghost" href="/extension">Get Chrome extension</a>
			</div>
		</div>
		<div class="about__hero-stats">
			{#each stats as stat}
				<div class="about__stat">
					<p class="about__stat-value">{stat.value}</p>
					<p class="about__stat-label">{stat.label}</p>
				</div>
			{/each}
		</div>
	</div>

	<div class="about__features">
		<h2>Core Features</h2>
		<div class="about__features-grid">
			{#each features as feature}
				<article class="about__feature-card">
					<div class="about__feature-icon">{feature.icon}</div>
					<h3>{feature.title}</h3>
					<p>{feature.description}</p>
				</article>
			{/each}
		</div>
	</div>

	<div class="about__sections">
		<article class="about__section">
			<h2>How it works</h2>
			<div class="about__steps">
				<div class="about__step">
					<span class="about__step-number">1</span>
					<h3>Connect your sheets</h3>
					<p>Sign in with Google and grant access to the spreadsheets you want to monitor.</p>
				</div>
				<div class="about__step">
					<span class="about__step-number">2</span>
					<h3>Configure monitoring</h3>
					<p>Set up validation rules, alerts, and automated workflows tailored to your needs.</p>
				</div>
				<div class="about__step">
					<span class="about__step-number">3</span>
					<h3>Get insights</h3>
					<p>Receive real-time alerts, view detailed reports, and apply AI-suggested fixes.</p>
				</div>
			</div>
		</article>

		<article class="about__section about__section--dark">
			<h2>Open Source</h2>
			<p class="about__section-text">
				Mangler is open source and available on GitHub. We believe in transparency and community-driven development. Contribute, report issues, or fork the project to customize it for your needs.
			</p>
			<div class="about__github-cta">
				<a href="https://github.com/noppud/mangler.finance" target="_blank" rel="noopener noreferrer" class="about__github-link">
					<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="24" height="24">
						<path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
					</svg>
					<div>
						<p class="about__github-title">github.com/noppud/mangler.finance</p>
						<p class="about__github-desc">Star, fork, or contribute to the project</p>
					</div>
				</a>
			</div>
		</article>

		<article class="about__section">
			<h2>Enterprise Ready</h2>
			<p class="about__section-text">
				Built for scale and security, Mangler handles everything from small team spreadsheets to enterprise-wide data operations.
			</p>
			<ul class="about__checklist">
				<li>SOC 2 Type II compliant infrastructure</li>
				<li>End-to-end encryption for all data transfers</li>
				<li>GDPR and CCPA compliant data handling</li>
				<li>99.9% uptime SLA guarantee</li>
				<li>24/7 enterprise support</li>
				<li>Custom deployment options available</li>
			</ul>
		</article>
	</div>

	<div class="about__cta">
		<h2>Ready to transform your spreadsheet operations?</h2>
		<p>Join thousands of teams using Mangler to maintain data integrity and automate their workflows.</p>
		<div class="about__cta-buttons">
			<a href="/login" class="about__btn about__btn--primary about__btn--large">Start free trial</a>
			<a href="/chat" class="about__btn about__btn--secondary about__btn--large">Try the demo</a>
		</div>
	</div>
</section>

<style>
	.about {
		max-width: 1200px;
		margin: 0 auto;
	}

	.about__hero {
		padding: clamp(2rem, 4vw, 3.5rem);
		border-radius: 2rem;
		background: radial-gradient(circle at top left, rgba(53, 255, 184, 0.18), transparent 55%),
			linear-gradient(135deg, rgba(6, 16, 12, 0.95), rgba(16, 39, 31, 0.9));
		border: 1px solid rgba(85, 193, 151, 0.35);
		box-shadow: 0 45px 80px rgba(3, 10, 8, 0.65);
		margin-bottom: 3rem;
	}

	.about__eyebrow-row {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		margin-bottom: 1rem;
	}

	.about__eyebrow {
		font-size: 0.85rem;
		text-transform: uppercase;
		letter-spacing: 0.35em;
		color: rgba(183, 246, 218, 0.6);
		margin: 0;
	}

	.about__badge {
		padding: 0.25rem 0.75rem;
		border-radius: 999px;
		font-size: 0.75rem;
		text-transform: uppercase;
		letter-spacing: 0.2em;
		background: rgba(60, 236, 163, 0.15);
		border: 1px solid rgba(60, 236, 163, 0.5);
		color: #c9ffe7;
	}

	h1 {
		font-size: clamp(2.4rem, 4vw, 3.6rem);
		margin: 0 0 1rem;
		color: #f6fff9;
		letter-spacing: -0.04em;
		line-height: 1.1;
	}

	h2 {
		font-size: clamp(1.8rem, 3vw, 2.4rem);
		margin: 0 0 1.5rem;
		color: #f6fff9;
	}

	.about__hero-text {
		font-size: 1.1rem;
		color: rgba(221, 248, 237, 0.85);
		margin-bottom: 2rem;
		line-height: 1.7;
		max-width: 65ch;
	}

	.about__actions {
		display: flex;
		flex-wrap: wrap;
		gap: 0.75rem;
		margin-bottom: 2rem;
	}

	.about__btn {
		border-radius: 999px;
		padding: 0.85rem 1.4rem;
		border: 1px solid transparent;
		font-weight: 600;
		cursor: pointer;
		text-decoration: none;
		text-align: center;
		transition: transform 150ms ease, box-shadow 150ms ease;
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
	}

	.about__btn--primary {
		background: linear-gradient(135deg, #2de28c, #69fabc);
		color: #02150d;
		box-shadow: 0 20px 30px rgba(47, 226, 140, 0.3);
	}

	.about__btn--secondary {
		background: rgba(47, 226, 140, 0.12);
		color: #c2ffe7;
		border-color: rgba(47, 226, 140, 0.4);
	}

	.about__btn--ghost {
		background: rgba(5, 12, 10, 0.55);
		color: #d2fbe9;
		border-color: rgba(91, 147, 129, 0.5);
	}

	.about__btn--large {
		padding: 1rem 2rem;
		font-size: 1.1rem;
	}

	.about__btn:hover {
		transform: translateY(-1px);
	}

	.about__hero-stats {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
		gap: 1rem;
		margin-top: 2rem;
		padding-top: 2rem;
		border-top: 1px solid rgba(85, 193, 151, 0.25);
	}

	.about__stat {
		text-align: center;
	}

	.about__stat-value {
		margin: 0;
		font-size: clamp(1.5rem, 3vw, 2rem);
		font-weight: 700;
		color: #4ef0b2;
	}

	.about__stat-label {
		margin: 0.25rem 0 0;
		font-size: 0.85rem;
		text-transform: uppercase;
		letter-spacing: 0.15em;
		color: rgba(183, 246, 218, 0.7);
	}

	.about__features {
		margin-bottom: 3rem;
	}

	.about__features-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
		gap: 1.5rem;
	}

	.about__feature-card {
		padding: 1.75rem;
		border-radius: 1.25rem;
		background: rgba(4, 9, 8, 0.75);
		border: 1px solid rgba(82, 136, 117, 0.4);
		box-shadow: 0 25px 50px rgba(2, 5, 4, 0.65);
		transition: transform 0.2s ease, box-shadow 0.2s ease;
	}

	.about__feature-card:hover {
		transform: translateY(-4px);
		box-shadow: 0 30px 60px rgba(2, 5, 4, 0.75);
	}

	.about__feature-icon {
		font-size: 2rem;
		margin-bottom: 1rem;
	}

	.about__feature-card h3 {
		margin: 0 0 0.75rem;
		font-size: 1.2rem;
		color: #f6fff9;
	}

	.about__feature-card p {
		margin: 0;
		color: rgba(211, 240, 230, 0.8);
		line-height: 1.6;
	}

	.about__sections {
		display: flex;
		flex-direction: column;
		gap: 2rem;
		margin-bottom: 3rem;
	}

	.about__section {
		padding: 2rem;
		border-radius: 1.5rem;
		background: rgba(4, 9, 8, 0.65);
		border: 1px solid rgba(82, 136, 117, 0.3);
	}

	.about__section--dark {
		background: radial-gradient(circle at center, rgba(60, 236, 163, 0.08), transparent 60%),
			rgba(4, 9, 8, 0.85);
		border-color: rgba(60, 236, 163, 0.3);
	}

	.about__section-text {
		font-size: 1.05rem;
		color: rgba(211, 240, 230, 0.85);
		line-height: 1.7;
		margin-bottom: 1.5rem;
		max-width: 65ch;
	}

	.about__steps {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
		gap: 2rem;
	}

	.about__step {
		position: relative;
	}

	.about__step-number {
		display: inline-flex;
		width: 2.5rem;
		height: 2.5rem;
		align-items: center;
		justify-content: center;
		background: linear-gradient(135deg, #2de28c, #69fabc);
		color: #02150d;
		font-weight: 700;
		border-radius: 50%;
		margin-bottom: 1rem;
	}

	.about__step h3 {
		margin: 0 0 0.5rem;
		font-size: 1.1rem;
		color: #f6fff9;
	}

	.about__step p {
		margin: 0;
		color: rgba(211, 240, 230, 0.8);
		line-height: 1.6;
	}

	.about__checklist {
		list-style: none;
		padding: 0;
		margin: 0;
		display: grid;
		gap: 0.75rem;
	}

	.about__checklist li {
		position: relative;
		padding-left: 2rem;
		color: rgba(211, 240, 230, 0.85);
		line-height: 1.6;
	}

	.about__checklist li::before {
		content: '✓';
		position: absolute;
		left: 0;
		color: #4ef0b2;
		font-weight: 700;
	}

	.about__github-cta {
		margin-top: 1.5rem;
	}

	.about__github-link {
		display: flex;
		align-items: center;
		gap: 1rem;
		padding: 1.25rem;
		border-radius: 1rem;
		background: rgba(6, 14, 12, 0.7);
		border: 1px solid rgba(78, 240, 178, 0.3);
		text-decoration: none;
		transition: transform 0.2s ease, border-color 0.2s ease;
	}

	.about__github-link:hover {
		transform: translateX(4px);
		border-color: rgba(78, 240, 178, 0.5);
	}

	.about__github-link svg {
		color: #4ef0b2;
	}

	.about__github-title {
		margin: 0 0 0.25rem;
		font-weight: 600;
		color: #f6fff9;
	}

	.about__github-desc {
		margin: 0;
		font-size: 0.9rem;
		color: rgba(211, 240, 230, 0.7);
	}

	.about__cta {
		text-align: center;
		padding: 3rem;
		border-radius: 1.5rem;
		background: radial-gradient(circle at center, rgba(53, 255, 184, 0.12), transparent 60%),
			linear-gradient(135deg, rgba(6, 16, 12, 0.9), rgba(16, 39, 31, 0.85));
		border: 1px solid rgba(85, 193, 151, 0.35);
	}

	.about__cta h2 {
		margin-bottom: 1rem;
	}

	.about__cta p {
		font-size: 1.1rem;
		color: rgba(221, 248, 237, 0.85);
		margin-bottom: 2rem;
		max-width: 50ch;
		margin-left: auto;
		margin-right: auto;
	}

	.about__cta-buttons {
		display: flex;
		gap: 1rem;
		justify-content: center;
		flex-wrap: wrap;
	}

	@media (max-width: 640px) {
		.about__actions {
			flex-direction: column;
		}

		.about__cta-buttons {
			flex-direction: column;
			align-items: center;
		}
	}
</style>