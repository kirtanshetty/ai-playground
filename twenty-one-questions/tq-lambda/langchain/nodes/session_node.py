"""
Node that reads the session key from the event.
"""

import json
from typing import Dict, Optional, Any


def read_session_key(event: Dict[str, Any]) -> Optional[str]:
    """
    Read the session key from the Lambda event.

    Supports multiple event formats:
    - Lambda Function URL HTTP events (POST with body, GET with query params)
    - Direct Lambda invocation

    Args:
        event: Lambda event object containing the input data

    Returns:
        str: The session key if found, None otherwise
    """
    if not isinstance(event, dict):
        return None

    # Check if it's a Lambda Function URL HTTP event
    if "body" in event:
        # POST request with body
        body = json.loads(event["body"]) if isinstance(event["body"], str) else event["body"]
        session_key = body.get("sessionKey") or body.get("session_key")
        return session_key
    elif "queryStringParameters" in event and event["queryStringParameters"]:
        # GET request with query parameters
        session_key = event["queryStringParameters"].get("sessionKey") or event[
            "queryStringParameters"
        ].get("session_key")
        return session_key
    else:
        # Direct invocation
        session_key = event.get("sessionKey") or event.get("session_key")
        return session_key
