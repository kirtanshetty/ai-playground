"""
Node for managing game state - handling answers and updating state.
"""

from typing import Dict, Any


def process_answer_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process the answer provided by the user and update the game state.
    
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
            last_qa["answer"] = answer.lower()  # Normalize to lowercase (yes/no)
        else:
            # No previous question, but answer provided - might be an error
            raise ValueError("Answer provided but no previous question found")
    # If no answer provided, that's fine - it's the first question or answer will come later
    
    return state


def update_state_with_question_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update game state with the new question from LLM.
    
    Args:
        state: State dictionary containing:
            - game_state: GameState object
            - next_question: The next question string from LLM
            
    Returns:
        Updated state dictionary
    """
    game_state = state.get("game_state")
    next_question = state.get("next_question")
    
    if not game_state:
        raise ValueError("game_state is required in state")
    if not next_question:
        raise ValueError("next_question is required in state")
    
    # Add the new question to the state (without answer yet - will be filled in next request)
    game_state.questions_and_answers.append({
        "question": next_question,
        "answer": "",  # Will be filled in next request when user provides answer
    })
    game_state.current_question_number += 1
    
    return state

