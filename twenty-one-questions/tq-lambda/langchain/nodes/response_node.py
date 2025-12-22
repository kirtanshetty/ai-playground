"""
Node for formatting the response to return to the user.
"""

import re
from typing import Dict, Any


def format_response_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format the response to return to the user.
    
    Response format:
    - question: The question text
    - guessingPersonality: Boolean indicating if this is a guess about a specific person
    - gameCompleted: Boolean indicating if game is over
    - victoryStatement/defeatStatement: End game messages
    
    Args:
        state: State dictionary containing:
            - game_state: GameState object
            - next_question: The next question string
            - guessing_personality: Boolean from LLM
            - session_key: Session key
            
    Returns:
        Updated state dictionary with:
            - response: Formatted response dictionary
    """
    game_state = state.get("game_state")
    next_question = state.get("next_question")
    guessing_personality = state.get("guessing_personality", False)
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
    
    # Check if the last question was a correct guess
    # Must have guessingPersonality=true AND answer="yes" AND valid person name
    last_qa = game_state.questions_and_answers[-1] if game_state.questions_and_answers else None
    
    from langchain.nodes.llm_node import is_valid_person_name
    
    # Validate that we have a proper person name (not a phrase like "Involved In Entertainment")
    has_valid_target = (
        game_state.target_person is not None and 
        is_valid_person_name(game_state.target_person) and
        len(game_state.target_person.split()) <= 4  # Names typically 1-4 words
    )
    
    last_was_correct_guess = (
        last_qa and 
        last_qa.get("guessingPersonality", False) and 
        last_qa.get("answer", "").lower() in ["yes", "y"] and
        has_valid_target  # Must have valid target to be a correct guess
    )
    
    # Game is won if: completed AND last was a correct guess (which includes valid target check)
    game_won = is_completed and last_was_correct_guess
    
    # Game is lost if: reached max questions without correct guess
    game_lost = reached_max and not game_won
    
    # Final game completed status
    game_completed_status = is_completed or game_won or game_lost
    
    response = {
        "status": "success",
        "sessionKey": session_key,
        "questionNumber": game_state.current_question_number - 1,
        "totalQuestions": questions_asked,
        "gameCompleted": game_completed_status,
    }
    
    if game_completed_status:
        if game_won:
            # Victory! Extract target person if needed
            if not game_state.target_person and last_was_correct_guess and last_qa:
                question_text = last_qa.get("question", "")
                guess_patterns = [
                    r"is it (.+?)\??",
                    r"are you thinking of (.+?)\??",
                    r"are you (.+?)\??",
                ]
                
                for pattern in guess_patterns:
                    match = re.search(pattern, question_text, re.IGNORECASE)
                    if match:
                        guessed_name = match.group(1).strip()
                        guessed_name = re.sub(r'^["\']|["\']$', '', guessed_name).strip()
                        guessed_name = ' '.join(word.capitalize() for word in guessed_name.split())
                        
                        if is_valid_person_name(guessed_name):
                            game_state.target_person = guessed_name
                            break
            
            if game_state.target_person and is_valid_person_name(game_state.target_person):
                response["targetPerson"] = game_state.target_person
                response["victoryStatement"] = (
                    f"Ah, of course! I knew it all along. {game_state.target_person} - "
                    f"how could I have missed it? My powers of deduction are truly unmatched. "
                    f"Another victory for the master of the mind!"
                )
                response["question"] = None
                response["guessingPersonality"] = False
                response["gameCompleted"] = True
            else:
                # Shouldn't happen, but handle gracefully
                response["targetPerson"] = None
                response["defeatStatement"] = (
                    "The mists cloud my vision... I must admit defeat this time. "
                    "My powers have failed me."
                )
                response["question"] = None
                response["guessingPersonality"] = False
                response["gameCompleted"] = True
        elif game_lost:
            # Defeat - 21 questions exhausted
            response["targetPerson"] = None
            response["defeatStatement"] = (
                "The mists cloud my vision... I must admit defeat this time. "
                "My powers have failed me. I need to meditate more, to sharpen my senses "
                "and deepen my connection to the ethereal realm. Perhaps next time I will succeed."
            )
            response["question"] = None
            response["guessingPersonality"] = False
            response["gameCompleted"] = True
        else:
            # Game marked completed for other reasons
            response["question"] = None
            response["guessingPersonality"] = False
            response["gameCompleted"] = True
    else:
        # Game still in progress
        if not next_question:
            raise ValueError("next_question is required when game is not completed")
        
        response["question"] = next_question
        response["guessingPersonality"] = guessing_personality
    
    return {
        **state,
        "response": response,
    }
