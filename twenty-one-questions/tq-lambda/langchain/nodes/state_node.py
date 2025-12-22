"""
Node for managing game state - handling answers and updating state.
"""

from typing import Dict, Any


def process_answer_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process the answer provided by the user and update the game state.
    
    Game ends ONLY if:
    1. The previous question was a guess (guessingPersonality: true) AND answer is "yes"
    2. OR 21 questions have been exhausted
    
    If guessingPersonality was true but answer is "no", the game continues.
    
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
            last_qa["answer"] = answer_lower
            
            # Check if the last question was a guess (guessingPersonality: true)
            if last_qa.get("guessingPersonality", False):
                if answer_lower in ["yes", "y"]:
                    # Correct guess! Mark game as completed
                    game_state.game_completed = True
                    # Keep the target_person that was set when the guess was made
                else:
                    # Wrong guess - clear the target person and continue the game
                    game_state.target_person = None
                    # Game does NOT end - continue playing until 21 questions or correct guess
        else:
            raise ValueError("Answer provided but no previous question found")
    
    return state


def update_state_with_question_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update game state with the new question from LLM.
    
    Args:
        state: State dictionary containing:
            - game_state: GameState object
            - next_question: The next question string from LLM (or None if game completed)
            - guessing_personality: Boolean indicating if this is a guess
            - guessed_person: Name of the person if it's a guess
            
    Returns:
        Updated state dictionary
    """
    game_state = state.get("game_state")
    next_question = state.get("next_question")
    guessing_personality = state.get("guessing_personality", False)
    guessed_person = state.get("guessed_person")
    
    if not game_state:
        raise ValueError("game_state is required in state")
    
    # If next_question is None, game is completed - don't add anything
    if next_question is None:
        return state
    
    # Add the new question to the state (without answer yet - will be filled in next request)
    game_state.questions_and_answers.append({
        "question": next_question,
        "answer": "",  # Will be filled in next request when user provides answer
        "guessingPersonality": guessing_personality,  # Whether this is a guess about a specific person
    })
    
    # If it's a guess, store the guessed person name
    if guessing_personality and guessed_person:
        game_state.target_person = guessed_person
    
    game_state.current_question_number += 1
    
    # Check if we've reached max questions
    MAX_QUESTIONS = 21
    if len(game_state.questions_and_answers) >= MAX_QUESTIONS and not game_state.game_completed:
        # Mark game as lost (reached max questions without guessing correctly)
        game_state.game_completed = True
    
    return state
