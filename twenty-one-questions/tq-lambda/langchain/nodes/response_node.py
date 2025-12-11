"""
Node for formatting the response to return to the user.
"""

import re
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
    # Game is won if: completed AND we have a valid target person (correctly guessed)
    # Game is lost if: reached max questions AND no target person (didn't guess correctly)
    # Check if the last question was a guess that was answered "yes"
    last_qa = game_state.questions_and_answers[-1] if game_state.questions_and_answers else None
    last_was_correct_guess = (
        last_qa and 
        last_qa.get("is_guess", False) and 
        last_qa.get("answer", "").lower() in ["yes", "y"]
    )
    
    # Only mark as won if we have a valid target person (not just any extracted text)
    # Import the validation function to check if target_person is valid
    from langchain.nodes.llm_node import is_valid_person_name
    
    has_valid_target = game_state.target_person is not None and is_valid_person_name(game_state.target_person)
    game_won = is_completed and has_valid_target and last_was_correct_guess
    game_lost = (reached_max or is_completed) and not has_valid_target
    
    # Determine gameCompleted status - should be True if game is completed OR won OR lost
    # But recalculate after we check for valid target person
    game_completed_status = is_completed or game_won or game_lost
    
    response = {
        "status": "success",
        "sessionKey": session_key,
        "questionNumber": game_state.current_question_number - 1,
        "totalQuestions": questions_asked,
        "gameCompleted": game_completed_status,
    }
    
    # If game is completed (won or lost), handle completion - don't require next_question
    if game_completed_status:
        # If game is won, add victory details
        if game_won:
            # Victory! The personality was guessed correctly
            # If target_person is not set but we have a correct guess, extract it from the last question
            if not game_state.target_person and last_was_correct_guess and last_qa:
                # Import validation function
                from langchain.nodes.llm_node import is_valid_person_name
                
                # Try to extract the person's name from the question
                question_text = last_qa.get("question", "")
                # Try common guess patterns (only patterns that indicate a guess, not regular questions)
                guess_patterns = [
                    r"is it (.+?)\??",  # "Is it Albert Einstein?"
                    r"are you thinking of (.+?)\??",  # "Are you thinking of Albert Einstein?"
                    r"are you (.+?)\??",  # "Are you Albert Einstein?"
                ]
                
                for pattern in guess_patterns:
                    match = re.search(pattern, question_text, re.IGNORECASE)
                    if match:
                        guessed_name = match.group(1).strip()
                        guessed_name = re.sub(r'^["\']|["\']$', '', guessed_name).strip()
                        guessed_name = ' '.join(word.capitalize() for word in guessed_name.split())
                        
                        # Validate that it's actually a person's name before using it
                        if is_valid_person_name(guessed_name):
                            game_state.target_person = guessed_name
                            break
            
            # Only set targetPerson if we have a valid person name
            from langchain.nodes.llm_node import is_valid_person_name
            if game_state.target_person and is_valid_person_name(game_state.target_person):
                response["targetPerson"] = game_state.target_person
                response["victoryStatement"] = (
                    f"Ah, of course! I knew it all along. {game_state.target_person} - "
                    f"how could I have missed it? My powers of deduction are truly unmatched. "
                    f"Another victory for the master of the mind!"
                )
                response["question"] = None  # No more questions
                response["gameCompleted"] = True  # Explicitly set to ensure it's True
            else:
                # If we don't have a valid target person, this shouldn't be a win - treat as loss
                response["targetPerson"] = None
                response["defeatStatement"] = (
                    "The mists cloud my vision... I must admit defeat this time. "
                    "My powers have failed me. I need to meditate more, to sharpen my senses "
                    "and deepen my connection to the ethereal realm. Perhaps next time I will succeed."
                )
                response["question"] = None  # No more questions
                response["gameCompleted"] = True
        elif game_lost:
            # Defeat - 21 questions reached without guessing correctly
            response["targetPerson"] = None
            response["defeatStatement"] = (
                "The mists cloud my vision... I must admit defeat this time. "
                "My powers have failed me. I need to meditate more, to sharpen my senses "
                "and deepen my connection to the ethereal realm. Perhaps next time I will succeed."
            )
            response["question"] = None  # No more questions
            response["gameCompleted"] = True
        else:
            # Game is marked as completed but not won or lost - this shouldn't happen, but handle gracefully
            response["question"] = None
            response["gameCompleted"] = True
    else:
        # Game still in progress - require next_question
        if not next_question:
            raise ValueError("next_question is required when game is not completed")
        response["question"] = next_question
        
        # Check if this is a guess (from LLM node)
        is_guess = state.get("is_guess", False)
        if is_guess:
            response["guess"] = True
    
    return {
        **state,
        "response": response,
    }

