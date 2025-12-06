<script lang="ts">
	export let questionNumber: number;
	export let MAX_QUESTIONS: number;
	// These props are passed from parent but not used in this component's template
	export let gameCompleted: boolean = false;
	export let targetPerson: string | null | undefined = null;

	$: questionsRemaining = MAX_QUESTIONS - questionNumber + 1;
	$: progressPercentage = ((questionNumber - 1) / MAX_QUESTIONS) * 100;
</script>

<div class="game-status">
	<div class="status-header">
		<div class="questions-info">
			<span class="questions-remaining">{questionsRemaining}</span>
			<span class="questions-label">questions remaining</span>
		</div>
		<div class="progress-bar-container">
			<div class="progress-bar" style="width: {progressPercentage}%"></div>
		</div>
	</div>
</div>

<style>
	.game-status {
		background: transparent;
		border-radius: 0;
		border: none;
		padding: 0;
		box-shadow: none;
		margin-bottom: var(--spacing-sm);
	}

	.status-header {
		display: flex;
		align-items: center;
		gap: var(--spacing-md);
		flex-wrap: wrap;
		width: 100%;
	}

	.questions-info {
		display: flex;
		align-items: baseline;
		gap: var(--spacing-xs);
	}

	.questions-remaining {
		font-size: 2rem;
		font-weight: 800;
		background: linear-gradient(135deg, var(--color-primary), var(--color-mystical));
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		background-clip: text;
		text-shadow: 0 0 15px var(--color-primary-glow);
		animation: pulse-number 2s ease-in-out infinite;
	}

	@keyframes pulse-number {
		0%, 100% {
			opacity: 1;
		}
		50% {
			opacity: 0.8;
		}
	}

	.questions-label {
		font-size: 0.9rem;
		color: var(--color-text-muted);
		text-transform: uppercase;
		letter-spacing: 0.5px;
	}

	.progress-bar-container {
		flex: 1;
		min-width: 200px;
		height: 8px;
		background: transparent;
		border-radius: 4px;
		overflow: hidden;
	}

	.progress-bar {
		height: 100%;
		background: linear-gradient(90deg, var(--color-primary), var(--color-mystical), #c084fc);
		border-radius: 4px;
		transition: width 0.3s ease;
		position: relative;
		overflow: hidden;
	}

	.progress-bar::after {
		content: '';
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
		animation: shimmer 2s infinite;
	}

	@keyframes shimmer {
		0% {
			transform: translateX(-100%);
		}
		100% {
			transform: translateX(100%);
		}
	}
</style>

