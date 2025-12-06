"""
Node for formatting the response to return to the user.
"""

from typing import Dict, Any


def format_response_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format the response to return to the user.
    Includes victory/defeat statements when game is completed.
    
    Args:
        state: State dictionary containing:
            - game_state: GameState object
            - next_question: The next question string
            - session_key: Session key
            
    Returns:
        Updated state dictionary with:
            - response: Formatted response dictionary
    """
    game_state = state.get("game_state")
    next_question = state.get("next_question")
    session_key = state.get("session_key")
    
    if not game_state:
        raise ValueError("game_state is required in state")
    if not session_key:
        raise ValueError("session_key is required in state")
    
    MAX_QUESTIONS = 21
    
    # Check if game is completed
    is_completed = game_state.game_completed
    questions_asked = len(game_state.questions_and_answers)
    reached_max = questions_asked >= MAX_QUESTIONS
    
    # Determine if game is won or lost
    # Game is won if: completed AND we have a target person (correctly guessed)
    # Game is lost if: reached max questions AND no target person (didn't guess correctly)
    game_won = is_completed and game_state.target_person is not None
    game_lost = (reached_max or is_completed) and game_state.target_person is None
    
    response = {
        "status": "success",
        "sessionKey": session_key,
        "questionNumber": game_state.current_question_number - 1,
        "totalQuestions": questions_asked,
        "gameCompleted": is_completed or game_lost,
    }
    
    # If game is completed, add completion details
    if game_won:
        # Victory! The personality was guessed correctly
        response["targetPerson"] = game_state.target_person
        response["victoryStatement"] = (
            f"Ah, of course! I knew it all along. {game_state.target_person} - "
            f"how could I have missed it? My powers of deduction are truly unmatched. "
            f"Another victory for the master of the mind!"
        )
        response["question"] = None  # No more questions
    elif game_lost:
        # Defeat - 21 questions reached without guessing correctly
        response["targetPerson"] = None
        response["defeatStatement"] = (
            "The mists cloud my vision... I must admit defeat this time. "
            "My powers have failed me. I need to meditate more, to sharpen my senses "
            "and deepen my connection to the ethereal realm. Perhaps next time I will succeed."
        )
        response["question"] = None  # No more questions
    else:
        # Game still in progress
        if not next_question:
            raise ValueError("next_question is required when game is not completed")
        response["question"] = next_question
    
    return {
        **state,
        "response": response,
    }

