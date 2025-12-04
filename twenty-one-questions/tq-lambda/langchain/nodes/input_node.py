"""
Node for processing and validating input from the event.
"""

from typing import Dict, Any


def process_input_node(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process and validate input from the Lambda event.
    
    Args:
        event: Lambda event dictionary
        
    Returns:
        State dictionary with:
            - session_key: Session key from event
            - answer: Optional answer from event
            - email: Optional email from event
            
    Raises:
        ValueError: If event is invalid or session_key is missing
    """
    if not isinstance(event, dict):
        raise ValueError("Event must be a dictionary")
    
    session_key = event.get("sessionKey")
    answer = event.get("answer")
    email = event.get("email")
    
    if not session_key:
        raise ValueError("Missing session key - please provide a sessionKey in the event")
    
    return {
        "session_key": session_key,
        "answer": answer,
        "email": email,
    }

