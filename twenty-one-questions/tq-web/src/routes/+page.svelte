<script>
	import GameBoard from '../lib/components/GameBoard.svelte';
	import MentalistFigure from '../lib/components/MentalistFigure.svelte';
</script>

<div class="page-container">
	<header class="header">
		<h1 class="title">twenty one questions</h1>
	</header>
	
	<div class="main-content">
		<div class="left-panel">
			<MentalistFigure />
		</div>
		
		<div class="right-panel">
			<GameBoard />
		</div>
	</div>
</div>

<style>
	.page-container {
		display: flex;
		flex-direction: column;
		min-height: 100vh;
	}

	.header {
		text-align: center;
		position: relative;
		padding: var(--spacing-md) 0;
		width: 100%;
	}

	.main-content {
		display: flex;
		flex-direction: row;
		flex: 1;
		gap: var(--spacing-md);
		position: relative;
		align-items: flex-start;
	}

	.left-panel {
		flex: 1;
		display: flex;
		justify-content: center;
		align-items: flex-start;
		padding: var(--spacing-md) var(--spacing-sm);
	}

	.right-panel {
		flex: 1;
		display: flex;
		flex-direction: column;
		gap: var(--spacing-md);
		padding: var(--spacing-md) var(--spacing-sm);
		min-width: 0;
		align-items: stretch;
	}

	.title {
		font-size: 3rem;
		font-weight: 800;
		background: linear-gradient(135deg, var(--color-primary), var(--color-mystical), #c084fc);
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		background-clip: text;
		margin: 0 0 var(--spacing-xs) 0;
		text-shadow: 0 0 30px var(--color-primary-glow);
		animation: title-glow 3s ease-in-out infinite;
		letter-spacing: 2px;
	}

	@keyframes title-glow {
		0%, 100% {
			filter: drop-shadow(0 0 10px var(--color-primary-glow));
		}
		50% {
			filter: drop-shadow(0 0 20px var(--color-primary-glow));
		}
	}

	.subtitle {
		color: var(--color-mystical);
		font-size: 1.2rem;
		font-weight: 600;
		margin: var(--spacing-sm) 0;
		text-shadow: 0 0 10px var(--color-mystical-glow);
		font-style: italic;
	}

	.tagline {
		color: var(--color-text-muted);
		font-size: 0.95rem;
		margin-top: var(--spacing-xs);
		font-style: italic;
	}

	@media (max-width: 968px) {
		.main-content {
			flex-direction: column;
		}

		.left-panel,
		.right-panel {
			flex: 1 1 auto;
		}

		.title {
			font-size: 2.5rem;
		}
	}
</style>

