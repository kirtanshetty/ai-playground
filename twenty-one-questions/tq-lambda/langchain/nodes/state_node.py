"""
Node for managing game state - handling answers and updating state.
"""

from typing import Dict, Any


def process_answer_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process the answer provided by the user and update the game state.
    If the previous question was a guess and the answer is "yes", mark game as completed.
    If the answer is "no", clear the guessed person (it was wrong).
    
    Args:
        state: State dictionary containing:
            - game_state: GameState object
            - answer: Optional answer string (yes/no)
            
    Returns:
        Updated state dictionary
        
    Raises:
        ValueError: If answer is provided but no previous question exists
    """
    game_state = state.get("game_state")
    answer = state.get("answer")
    
    if not game_state:
        raise ValueError("game_state is required in state")
    
    # If answer is provided, add it to the previous question in the state
    if answer:
        # Get the last question (if any)
        if game_state.questions_and_answers:
            last_qa = game_state.questions_and_answers[-1]
            # Update the answer for the last question
            answer_lower = answer.lower().strip()
            last_qa["answer"] = answer_lower  # Normalize to lowercase (yes/no)
            
            # Check if the last question was a guess
            if last_qa.get("is_guess", False):
                if answer_lower in ["yes", "y"]:
                    # Correct guess! Mark game as completed
                    game_state.game_completed = True
                    # Keep the target_person that was set when the guess was made
                else:
                    # Wrong guess - clear the target person and continue
                    game_state.target_person = None
        else:
            # No previous question, but answer provided - might be an error
            raise ValueError("Answer provided but no previous question found")
    # If no answer provided, that's fine - it's the first question or answer will come later
    
    return state


def update_state_with_question_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update game state with the new question from LLM.
    Handles both regular questions and guesses.
    Skips if next_question is None (game completed).
    
    Args:
        state: State dictionary containing:
            - game_state: GameState object
            - next_question: The next question string from LLM (or None if game completed)
            - is_guess: Boolean indicating if this is a guess
            - guessed_person: Name of the person if it's a guess
            
    Returns:
        Updated state dictionary
    """
    game_state = state.get("game_state")
    next_question = state.get("next_question")
    is_guess = state.get("is_guess", False)
    guessed_person = state.get("guessed_person")
    
    if not game_state:
        raise ValueError("game_state is required in state")
    
    # If next_question is None, game is completed - don't add anything
    if next_question is None:
        return state
    
    # Add the new question/guess to the state (without answer yet - will be filled in next request)
    game_state.questions_and_answers.append({
        "question": next_question,
        "answer": "",  # Will be filled in next request when user provides answer
        "is_guess": is_guess,  # Mark if this is a guess
    })
    
    # If it's a guess, store the guessed person name
    if is_guess and guessed_person:
        game_state.target_person = guessed_person
    
    game_state.current_question_number += 1
    
    # Check if we've reached max questions
    MAX_QUESTIONS = 21
    if len(game_state.questions_and_answers) >= MAX_QUESTIONS and not game_state.game_completed:
        # Mark game as lost (reached max questions without guessing correctly)
        game_state.game_completed = True
    
    return state

