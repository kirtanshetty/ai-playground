<script lang="ts">
	import { onMount } from 'svelte';
	import QuestionDisplay from './QuestionDisplay.svelte';
	import AnswerButtons from './AnswerButtons.svelte';
	import GameHistory from './GameHistory.svelte';
	import GameStatus from './GameStatus.svelte';
	
	// Import types
	import type { QuestionAnswer, GameResponse } from '../types/game';

	let currentQuestion: string = '';
	let questionsAndAnswers: QuestionAnswer[] = [];
	let questionNumber: number = 1;
	let isLoading: boolean = false;
	let gameStarted: boolean = false;
	let gameCompleted: boolean = false;
	let targetPerson: string | null = null;
	let sessionKey: string | null = null;
	let victoryStatement: string | null = null;
	let defeatStatement: string | null = null;
	let currentQuestionIsGuess: boolean = false;

	const MAX_QUESTIONS = 21;

	// Generate a unique session key
	function generateSessionKey(): string {
		return `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
	}

	async function startGame(): Promise<void> {
		gameStarted = true;
		isLoading = true;
		sessionKey = generateSessionKey();

		try {
			// Call API to get first question
			const response = await fetch('/api/game', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					sessionKey,
				}),
			});

			if (!response.ok) {
				const error: GameResponse = await response.json();
				throw new Error(error.message || 'Failed to start game');
			}

			const data: GameResponse = await response.json();
			if (data.error) {
				throw new Error(data.message || data.error);
			}

			currentQuestion = data.question || '';
			questionNumber = data.questionNumber || 1;
			currentQuestionIsGuess = data.guess || false;
		} catch (error) {
			console.error('Error starting game:', error);
			const errorMessage = error instanceof Error ? error.message : 'Unknown error';
			alert(`Failed to start game: ${errorMessage}`);
			gameStarted = false;
		} finally {
			isLoading = false;
		}
	}

	async function submitAnswer(answer: string): Promise<void> {
		if (!currentQuestion || isLoading) return;

		// Add to history
		questionsAndAnswers = [...questionsAndAnswers, { question: currentQuestion, answer }];
		questionNumber += 1;

		// Check if game is complete (this should be handled by the API response)
		// But we'll also check here as a safety measure
		if (questionNumber > MAX_QUESTIONS) {
			gameCompleted = true;
			return;
		}

		// Get next question
		isLoading = true;
		currentQuestion = '';

		try {
			// Call API to get next question based on history
			const response = await fetch('/api/game', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					sessionKey,
					answer,
					questionNumber,
				}),
			});

			if (!response.ok) {
				const error: GameResponse = await response.json();
				throw new Error(error.message || 'Failed to get next question');
			}

			const data: GameResponse = await response.json();
			if (data.error) {
				throw new Error(data.message || data.error);
			}

			// Check if game is completed (target person found or game lost)
			// This can happen if:
			// 1. A guess was answered with "yes" (game won)
			// 2. Max questions reached without correct guess (game lost)
			if (data.gameCompleted) {
				gameCompleted = true;
				targetPerson = data.targetPerson || null;
				victoryStatement = data.victoryStatement || null;
				defeatStatement = data.defeatStatement || null;
				return;
			}

			currentQuestion = data.question || '';
			questionNumber = data.questionNumber || questionNumber;
			currentQuestionIsGuess = data.guess || false;
		} catch (error) {
			console.error('Error submitting answer:', error);
			const errorMessage = error instanceof Error ? error.message : 'Unknown error';
			alert(`Failed to submit answer: ${errorMessage}`);
		} finally {
			isLoading = false;
		}
	}

	function resetGame(): void {
		currentQuestion = '';
		questionsAndAnswers = [];
		questionNumber = 1;
		gameStarted = false;
		gameCompleted = false;
		targetPerson = null;
		sessionKey = null;
		victoryStatement = null;
		defeatStatement = null;
		currentQuestionIsGuess = false;
	}
</script>

<div class="game-board">
	{#if !gameStarted}
		<div class="start-screen">
			<GameStatus 
				{questionNumber} 
				{MAX_QUESTIONS} 
				{gameCompleted}
				{targetPerson}
			/>
			
			<div class="rules">
				<h2>Rules of the Ritual</h2>
				<ul>
					<li>Think of a famous REAL PERSON (not fictional)</li>
					<li>I shall probe your mind with 21 questions</li>
					<li>Answer truthfully, for I sense deception</li>
					<li>Through the veil of thought, I will divine their identity</li>
				</ul>
			</div>
			<button class="start-button" on:click={startGame}>
				Begin the Reading
			</button>
		</div>
	{:else if gameCompleted}
		<div class="game-completed">
			{#if victoryStatement}
				<h2>The Vision is Clear</h2>
				<p class="result statement">{victoryStatement}</p>
				{#if targetPerson}
					<p class="result person">The person was: <strong>{targetPerson}</strong></p>
				{/if}
			{:else if defeatStatement}
				<h2>The Mists Cloud My Vision</h2>
				<p class="result statement">{defeatStatement}</p>
			{:else}
				<h2>The Vision is Clear</h2>
				{#if targetPerson}
					<p class="result">I see... I see... <strong>{targetPerson}</strong></p>
				{:else}
					<p class="result">The mists cloud my vision... I could not pierce the veil this time.</p>
				{/if}
			{/if}
			<button class="reset-button" on:click={resetGame}>
				Seek Another Reading
			</button>
		</div>
	{:else}
		<div class="merged-box">
			<GameStatus 
				{questionNumber} 
				{MAX_QUESTIONS} 
				{gameCompleted}
				{targetPerson}
			/>
			
			<QuestionDisplay 
				{currentQuestion} 
				{questionNumber}
				{isLoading}
			/>
			
			{#if currentQuestion && !isLoading}
				<AnswerButtons on:answer={(e) => submitAnswer(e.detail)} />
			{/if}
		</div>
	{/if}

	{#if questionsAndAnswers.length > 0}
		<GameHistory {questionsAndAnswers} />
	{/if}
</div>

<style>
	.game-board {
		display: flex;
		flex-direction: column;
		gap: var(--spacing-lg);
	}

	.merged-box {
		background: transparent;
		padding: var(--spacing-md) var(--spacing-sm);
		display: flex;
		flex-direction: column;
		gap: var(--spacing-md);
	}

	.start-screen {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: var(--spacing-md);
		padding: var(--spacing-md) var(--spacing-sm);
		background: transparent;
		position: relative;
		overflow: hidden;
	}

	.start-screen::before {
		content: '';
		position: absolute;
		top: -50%;
		left: -50%;
		width: 200%;
		height: 200%;
		background: transparent;
		opacity: 0;
		animation: rotate-glow 10s linear infinite;
	}

	@keyframes rotate-glow {
		from {
			transform: rotate(0deg);
		}
		to {
			transform: rotate(360deg);
		}
	}

	.rules {
		text-align: center;
		max-width: 500px;
	}

	.rules h2 {
		font-size: 1.5rem;
		margin-bottom: var(--spacing-md);
	}

	.rules ul {
		list-style: none;
		text-align: left;
		display: inline-block;
	}

	.rules li {
		padding: var(--spacing-xs) 0;
		padding-left: var(--spacing-md);
		position: relative;
	}

	.rules li::before {
		content: "✓";
		position: absolute;
		left: 0;
		color: var(--color-success);
		font-weight: bold;
	}

	.start-button {
		padding: var(--spacing-md) var(--spacing-xl);
		font-size: 1.2rem;
		background: linear-gradient(135deg, var(--color-primary), var(--color-mystical));
		color: white;
		box-shadow: 0 0 20px var(--color-primary-glow);
		position: relative;
		z-index: 1;
	}

	.start-button:hover:not(:disabled) {
		background: linear-gradient(135deg, var(--color-primary-hover), #7c3aed);
		transform: translateY(-2px);
		box-shadow: 0 4px 25px var(--color-primary-glow);
	}

	.game-active {
		display: flex;
		flex-direction: column;
		gap: var(--spacing-lg);
	}

	.game-completed {
		text-align: center;
		padding: var(--spacing-md) var(--spacing-sm);
		background: transparent;
		position: relative;
	}

	.game-completed h2 {
		font-size: 2rem;
		margin-bottom: var(--spacing-md);
		background: linear-gradient(135deg, var(--color-primary), var(--color-mystical));
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		background-clip: text;
		text-shadow: 0 0 20px var(--color-primary-glow);
	}

	.result {
		font-size: 1.2rem;
		margin-bottom: var(--spacing-lg);
	}

	.result.statement {
		font-size: 1.3rem;
		line-height: 1.6;
		margin-bottom: var(--spacing-md);
		font-style: italic;
	}

	.result.person {
		font-size: 1.4rem;
		margin-top: var(--spacing-md);
	}

	.result strong {
		color: var(--color-success);
		font-size: 1.4rem;
	}

	.reset-button {
		padding: var(--spacing-md) var(--spacing-xl);
		font-size: 1.1rem;
		background: var(--color-primary);
		color: white;
	}

	.reset-button:hover:not(:disabled) {
		background: var(--color-primary-hover);
		transform: translateY(-2px);
		box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
	}
</style>

