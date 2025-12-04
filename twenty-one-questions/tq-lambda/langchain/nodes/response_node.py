"""
Node for formatting the response to return to the user.
"""

from typing import Dict, Any


def format_response_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format the response to return to the user.
    
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
    if not next_question:
        raise ValueError("next_question is required in state")
    if not session_key:
        raise ValueError("session_key is required in state")
    
    response = {
        "status": "success",
        "sessionKey": session_key,
        "question": next_question,
        "questionNumber": game_state.current_question_number - 1,
        "totalQuestions": len(game_state.questions_and_answers),
    }
    
    return {
        **state,
        "response": response,
    }

