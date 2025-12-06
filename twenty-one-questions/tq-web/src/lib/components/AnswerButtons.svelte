<script lang="ts">
	import { createEventDispatcher } from 'svelte';

	const dispatch = createEventDispatcher();

	function handleAnswer(answer: string): void {
		dispatch('answer', answer);
	}
</script>

<div class="answer-buttons">
	<button 
		class="answer-button yes-button" 
		on:click={() => handleAnswer('Yes')}
	>
		<span class="button-icon">✓</span>
		<span class="button-text">Yes</span>
	</button>
	
	<button 
		class="answer-button no-button" 
		on:click={() => handleAnswer('No')}
	>
		<span class="button-icon">✗</span>
		<span class="button-text">No</span>
	</button>
</div>

<style>
	.answer-buttons {
		display: flex;
		gap: var(--spacing-md);
		justify-content: center;
		flex-wrap: wrap;
	}

	.answer-button {
		flex: 1;
		min-width: 150px;
		max-width: 250px;
		padding: var(--spacing-md) var(--spacing-sm);
		font-size: 1.2rem;
		display: flex;
		align-items: center;
		justify-content: center;
		gap: var(--spacing-sm);
		transition: all 0.2s ease;
	}

	.yes-button {
		background: linear-gradient(135deg, var(--color-success), #059669);
		color: white;
	}

	.yes-button:hover:not(:disabled) {
		background: linear-gradient(135deg, var(--color-success-hover), #047857);
		transform: translateY(-2px);
	}

	.no-button {
		background: linear-gradient(135deg, var(--color-danger), #dc2626);
		color: white;
	}

	.no-button:hover:not(:disabled) {
		background: linear-gradient(135deg, var(--color-danger-hover), #b91c1c);
		transform: translateY(-2px);
	}

	.button-icon {
		font-size: 1.5rem;
		font-weight: bold;
	}

	.button-text {
		font-weight: 600;
	}
</style>

