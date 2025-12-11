export interface QuestionAnswer {
	question: string;
	answer: string;
}

export interface GameResponse {
	status?: string;
	sessionKey?: string;
	question?: string;
	questionNumber?: number;
	totalQuestions?: number;
	gameCompleted?: boolean;
	guess?: boolean;
	targetPerson?: string | null;
	victoryStatement?: string | null;
	defeatStatement?: string | null;
	error?: string;
	message?: string;
}

