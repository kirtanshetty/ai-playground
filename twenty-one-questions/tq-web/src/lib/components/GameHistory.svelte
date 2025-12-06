<script>
	export let questionsAndAnswers;
</script>

<div class="game-history">
	<h3>Question History</h3>
	<div class="history-list">
		{#each questionsAndAnswers as qa, index}
			<div class="history-item">
				<div class="question-number-badge">Q{index + 1}</div>
				<div class="qa-content">
					<div class="question">{qa.question}</div>
					<div class="answer answer-{qa.answer.toLowerCase()}">
						{qa.answer}
					</div>
				</div>
			</div>
		{/each}
	</div>
</div>

<style>
	.game-history {
		background: transparent;
		padding: var(--spacing-md) var(--spacing-sm);
	}

	.game-history h3 {
		font-size: 1.3rem;
		margin-bottom: var(--spacing-md);
		color: var(--color-mystical);
		text-shadow: 0 0 10px var(--color-mystical-glow);
	}

	.history-list {
		display: flex;
		flex-direction: column;
		gap: var(--spacing-sm);
		max-height: 400px;
		overflow-y: auto;
	}

	.history-item {
		display: flex;
		gap: var(--spacing-md);
		padding: var(--spacing-md);
		background: transparent;
		border-radius: var(--border-radius);
	}

	.question-number-badge {
		flex-shrink: 0;
		width: 40px;
		height: 40px;
		display: flex;
		align-items: center;
		justify-content: center;
		background: linear-gradient(135deg, var(--color-primary), var(--color-mystical));
		color: white;
		border-radius: 50%;
		font-weight: 600;
		font-size: 0.9rem;
		box-shadow: 0 0 10px var(--color-primary-glow);
	}

	.qa-content {
		flex: 1;
		display: flex;
		flex-direction: column;
		gap: var(--spacing-xs);
	}

	.question {
		font-weight: 500;
		color: var(--color-text);
	}

	.answer {
		font-weight: 600;
		font-size: 0.95rem;
		padding: var(--spacing-xs) var(--spacing-sm);
		border-radius: 6px;
		display: inline-block;
		width: fit-content;
	}

	.answer-yes {
		background: rgba(16, 185, 129, 0.2);
		color: var(--color-success);
	}

	.answer-no {
		background: rgba(239, 68, 68, 0.2);
		color: var(--color-danger);
	}

	.history-list::-webkit-scrollbar {
		width: 8px;
	}

	.history-list::-webkit-scrollbar-track {
		background: transparent;
		border-radius: 4px;
	}

	.history-list::-webkit-scrollbar-thumb {
		background: var(--color-border);
		border-radius: 4px;
	}

	.history-list::-webkit-scrollbar-thumb:hover {
		background: var(--color-border);
	}
</style>

