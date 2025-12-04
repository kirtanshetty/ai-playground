"""
AWS Lambda handler for 21 questions game using LangChain chain.
"""

import sys
import os

# Add common-lib to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from langchain.chains.twenty_one_questions_chain import twenty_one_questions_chain


def lambda_handler(event, context):
    """
    AWS Lambda handler for 21 questions game.
    
    Args:
        event: Lambda event object containing the input data
        context: Lambda context object
        
    Returns:
        dict: Response containing the result or error
    """
    # Extract session key from event for all responses
    session_key = event.get("sessionKey") or event.get("session_key")
    
    try:
        # Run the chain with the event
        result = twenty_one_questions_chain.invoke(event)
        
        # Extract the response from the result
        response = result.get("response")
        
        if response:
            # Ensure session key is included (response_node should already include it, but ensure it's there)
            if session_key and "sessionKey" not in response:
                response["sessionKey"] = session_key
            return response
        else:
            return {
                "error": "Internal server error",
                "message": "Chain did not return a response",
                "sessionKey": session_key,
            }
    
    except ValueError as e:
        return {
            "error": "Invalid input",
            "message": str(e),
            "sessionKey": session_key,
        }
    except Exception as e:
        return {
            "error": "Internal server error",
            "message": str(e),
            "sessionKey": session_key,
        }
