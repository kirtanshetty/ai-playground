"""
AWS Lambda handler for 21 questions game using LangChain chain.

Supports both direct invocation and Lambda Function URL (HTTP) invocation.
"""

import sys
import os
import json

# Add common-lib to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from langchain.chains.twenty_one_questions_chain import twenty_one_questions_chain


def _create_http_response(status_code: int, body: dict) -> dict:
    """Create a Lambda Function URL compatible HTTP response."""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": json.dumps(body),
    }


def _is_function_url_event(event: dict) -> bool:
    """Check if this is a Lambda Function URL event (HTTP request)."""
    return "requestContext" in event and "http" in event.get("requestContext", {})


def _parse_function_url_body(event: dict) -> dict:
    """Parse the body from a Lambda Function URL event."""
    body = event.get("body", "{}")
    if event.get("isBase64Encoded", False):
        import base64
        body = base64.b64decode(body).decode("utf-8")
    return json.loads(body) if body else {}


def lambda_handler(event, context):
    """
    AWS Lambda handler for 21 questions game.
    
    Supports two invocation modes:
    1. Direct invocation (via AWS SDK) - event contains the payload directly
    2. Function URL (HTTP) - event contains HTTP request with body
    
    Args:
        event: Lambda event object containing the input data
        context: Lambda context object
        
    Returns:
        dict: Response containing the result or error
    """
    # Determine if this is a Function URL (HTTP) request
    is_http = _is_function_url_event(event)
    
    # Parse the input based on invocation type
    if is_http:
        input_data = _parse_function_url_body(event)
    else:
        input_data = event
    
    # Extract session key from input for all responses
    session_key = input_data.get("sessionKey") or input_data.get("session_key")
    
    try:
        # Run the chain with the input data
        result = twenty_one_questions_chain.invoke(input_data)
        
        # Extract the response from the result
        response = result.get("response")
        
        if response:
            # Ensure session key is included
            if session_key and "sessionKey" not in response:
                response["sessionKey"] = session_key
            
            if is_http:
                return _create_http_response(200, response)
            return response
        else:
            error_response = {
                "error": "Internal server error",
                "message": "Chain did not return a response",
                "sessionKey": session_key,
            }
            if is_http:
                return _create_http_response(500, error_response)
            return error_response
    
    except ValueError as e:
        error_response = {
            "error": "Invalid input",
            "message": str(e),
            "sessionKey": session_key,
        }
        if is_http:
            return _create_http_response(400, error_response)
        return error_response
    
    except Exception as e:
        error_response = {
            "error": "Internal server error",
            "message": str(e),
            "sessionKey": session_key,
        }
        if is_http:
            return _create_http_response(500, error_response)
        return error_response
