"""
Node that creates a prompt for the 21 questions game to identify a person.
"""

from typing import List, Dict, Optional, Any


def create_21_questions_prompt(
    questions_and_answers: Optional[List[Dict[str, str]]] = None,
    current_question_number: int = 1,
) -> str:
    """
    Create a prompt for the 21 questions game to identify a person.

    Args:
        questions_and_answers: List of previous Q&A pairs. Each dict should have:
            - 'question': The question asked
            - 'answer': The answer given
        current_question_number: The current question number (1-21)

    Returns:
        str: The formatted prompt for the LLM
    """
    base_prompt = """You are playing a game of "21 Questions to Identify the Person".
The goal is to identify a famous REAL PERSON (not fictional) by asking up to 21 yes/no questions.

IMPORTANT RULES:
- The person must be a REAL PERSON (not fictional characters, not animals, not objects) - you already know this, so don't ask about it
- You can only ask yes/no questions
- You have up to 21 questions total
- Try to narrow down the possibilities with each question
- Be strategic and ask questions that eliminate many possibilities at once
- Once you're confident, you can make a guess about who the person is
- When you make a guess, format it as: "Is it [Person's Name]?" or "Are you thinking of [Person's Name]?"
- If you are very confident about the person's identity, make a guess. Otherwise, ask another strategic yes/no question.
- LOSING CONDITION: If you reach 21 questions without correctly guessing the person, you lose the game

EXAMPLE GAME:
Here's an example of how a game might progress:

Question 1: Are you alive today?
Answer: No

Question 2: Were you born before 1900?
Answer: Yes

Question 3: Were you a scientist or inventor?
Answer: Yes

Question 4: Did you work in physics?
Answer: Yes

Question 5: Are you Albert Einstein?
Answer: Yes

In this example, the questions start broad (alive) and narrow down (time period, profession, field) until confident enough to guess. The final guess is formatted as "Are you Albert Einstein?" which is a yes/no question about a specific person. Note: We don't ask "Are you a real person?" because the rules already state the person must be real.

"""

    if questions_and_answers and len(questions_and_answers) > 0:
        prompt = base_prompt + "Here are the questions asked so far and their answers:\n\n"

        for i, qa in enumerate(questions_and_answers, 1):
            question = qa.get("question", "")
            answer = qa.get("answer", "")
            prompt += f"Question {i}: {question}\n"
            prompt += f"Answer: {answer}\n\n"

        # Encourage guessing when we're close to the limit or have enough information
        questions_remaining = 21 - len(questions_and_answers)
        
        if questions_remaining <= 3 or current_question_number >= 18:
            prompt += (
                f"Based on the information above, ask question "
                f"{current_question_number} to help identify the person.\n"
            )
            prompt += (
                "You are running out of questions. "
                "If you are confident about the person's identity, make a guess in the format: "
                "\"Is it [Person's Name]?\" or \"Are you thinking of [Person's Name]?\". "
                "When you make a guess, include 'guess:true' at the end of your response. "
                "Otherwise, ask one more strategic yes/no question."
            )
        else:
            prompt += (
                f"Based on the information above, ask question "
                f"{current_question_number} to help identify the person.\n"
            )
            prompt += (
                "Only ask one yes/no question. "
                "If you are very confident about the person's identity, you can make a guess "
                "in the format: \"Is it [Person's Name]?\" or \"Are you thinking of [Person's Name]?\". "
                "When you make a guess, include 'guess:true' at the end of your response. "
                "Otherwise, ask another strategic question."
            )
    else:
        prompt = (
            base_prompt
            + f"Ask question {current_question_number} to start identifying the person.\n"
        )
        prompt += "Only ask one yes/no question."

    return prompt


def prompt_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node that creates a prompt and stores it in flow_state.
    Skips prompt creation if game is already completed or max questions reached.
    
    Args:
        state: State dictionary containing:
            - game_state: GameState object with questions_and_answers and current_question_number
            
    Returns:
        Updated state dictionary with:
            - flow_state: Dictionary containing the prompt (or None if game completed)
    """
    game_state = state.get("game_state")
    if not game_state:
        raise ValueError("game_state is required in state")
    
    MAX_QUESTIONS = 21
    
    # Check if game is already completed or max questions reached
    if game_state.game_completed or len(game_state.questions_and_answers) >= MAX_QUESTIONS:
        # Don't create a prompt - game is over
        flow_state = dict(state.get("flow_state") or {})
        flow_state["prompt"] = None
        return {
            **state,
            "flow_state": flow_state,
        }
    
    # Build or extend the flow_state for non-persistent, per-flow values
    flow_state = dict(state.get("flow_state") or {})
    
    # Create and store the prompt in flow_state (not persisted to DB)
    prompt = create_21_questions_prompt(
        questions_and_answers=game_state.questions_and_answers,
        current_question_number=game_state.current_question_number,
    )
    flow_state["prompt"] = prompt
    
    return {
        **state,
        "flow_state": flow_state,
    }
