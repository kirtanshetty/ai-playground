<script>
	export let currentQuestion;
	export let questionNumber;
	export let isLoading;
</script>

<div class="question-display">
	<div class="question-number">
		Question {questionNumber} of 21
	</div>
	
	{#if isLoading}
		<div class="loading">
			<div class="spinner"></div>
			<p>Reading your thoughts...</p>
		</div>
	{:else if currentQuestion}
		<div class="question-text">
			{currentQuestion}
		</div>
	{/if}
</div>

<style>
	.question-display {
		background: transparent;
		border-radius: 0;
		border: none;
		padding: 0;
		min-height: 200px;
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
		text-align: center;
		box-shadow: none;
		position: relative;
	}

	.question-number {
		font-size: 0.9rem;
		color: var(--color-mystical);
		margin-bottom: var(--spacing-md);
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 1px;
		text-shadow: 0 0 10px var(--color-mystical-glow);
	}

	.question-text {
		font-size: 1.5rem;
		font-weight: 600;
		line-height: 1.5;
		color: var(--color-text);
		max-width: 800px;
		text-shadow: 0 0 5px rgba(139, 92, 246, 0.3);
	}

	.loading {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: var(--spacing-md);
	}

	.spinner {
		width: 40px;
		height: 40px;
		border: 4px solid var(--color-border);
		border-top-color: var(--color-primary);
		border-right-color: var(--color-mystical);
		border-radius: 50%;
		animation: spin 1s linear infinite;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}

	.loading p {
		color: var(--color-text-muted);
		font-size: 1rem;
	}
</style>

