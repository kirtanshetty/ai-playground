"""
State management nodes for the 21 questions game.
"""

from typing import Dict, Any

MAX_QUESTIONS = 21


def process_answer_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process user's answer to the previous question.
    
    Game ends when:
    1. User answers "yes" to a guess (guessingPersonality=true) -> WIN
    2. 21 questions exhausted -> LOSE
    """
    game_state = state.get("game_state")
    answer = state.get("answer")
    
    if not game_state:
        raise ValueError("game_state is required")
    
    if not answer:
        # No answer yet (first question)
        return state
    
    # Get the last question
    if not game_state.questions_and_answers:
        raise ValueError("No previous question to answer")
    
    last_qa = game_state.questions_and_answers[-1]
    answer_lower = answer.lower().strip()
    
    # Store the answer
    last_qa["answer"] = answer_lower
    
    # Check if this was a guess
    was_guess = last_qa.get("guessingPersonality", False)
    
    if was_guess and answer_lower in ["yes", "y"]:
        # Correct guess! Game won.
        game_state.game_completed = True
        # target_person should already be set from update_state_with_question_node
    elif was_guess:
        # Wrong guess - clear target person, continue game
        game_state.target_person = None
    
    return state


def update_state_with_question_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add the new question from LLM to game state.
    """
    game_state = state.get("game_state")
    next_question = state.get("next_question")
    guessing_personality = state.get("guessing_personality", False)
    guessed_person = state.get("guessed_person")
    
    if not game_state:
        raise ValueError("game_state is required")
    
    # Skip if no question (game already completed)
    if not next_question:
        return state
    
    # Add question to history
    game_state.questions_and_answers.append({
        "question": next_question,
        "answer": "",  # Will be filled when user answers
        "guessingPersonality": guessing_personality,
    })
    
    # Store guessed person if this is a guess
    if guessing_personality and guessed_person:
        game_state.target_person = guessed_person
    
    game_state.current_question_number += 1
    
    # Check if max questions reached
    if len(game_state.questions_and_answers) >= MAX_QUESTIONS:
        game_state.game_completed = True
    
    return state
