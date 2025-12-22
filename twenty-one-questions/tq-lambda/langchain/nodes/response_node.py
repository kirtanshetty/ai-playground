"""
Response formatting node.
"""

from typing import Dict, Any

MAX_QUESTIONS = 21


def format_response_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format the API response.
    
    Response includes:
    - question: Next question (or null if game over)
    - guessingPersonality: Is this a guess?
    - gameCompleted: Is game over?
    - targetPerson: Who was guessed (if won)
    - victoryStatement/defeatStatement: End game messages
    """
    game_state = state.get("game_state")
    next_question = state.get("next_question")
    guessing_personality = state.get("guessing_personality", False)
    session_key = state.get("session_key")
    
    if not game_state:
        raise ValueError("game_state is required")
    if not session_key:
        raise ValueError("session_key is required")
    
    questions_asked = len(game_state.questions_and_answers)
    
    # Determine game outcome
    game_won = False
    game_lost = False
    
    if game_state.game_completed:
        # Check why game ended
        if game_state.target_person:
            # We have a target person = we guessed correctly
            game_won = True
        else:
            # No target person = exhausted questions or wrong guesses
            game_lost = True
    
    # Build response
    response = {
        "status": "success",
        "sessionKey": session_key,
        "questionNumber": game_state.current_question_number,
        "totalQuestions": questions_asked,
        "gameCompleted": game_state.game_completed,
    }
    
    if game_won:
        response["question"] = None
        response["guessingPersonality"] = False
        response["targetPerson"] = game_state.target_person
        response["victoryStatement"] = (
            f"I knew it! {game_state.target_person}! "
            f"My powers of deduction are unmatched. Another victory!"
        )
    elif game_lost:
        response["question"] = None
        response["guessingPersonality"] = False
        response["targetPerson"] = None
        response["defeatStatement"] = (
            "The mists cloud my vision... I must admit defeat. "
            "My powers have failed me this time."
        )
    else:
        # Game in progress
        if not next_question:
            raise ValueError("next_question required when game not completed")
        
        response["question"] = next_question
        response["guessingPersonality"] = guessing_personality
    
    return {
        **state,
        "response": response,
    }
