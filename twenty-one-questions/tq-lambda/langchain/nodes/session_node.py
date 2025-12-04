"""
Node that reads the session key from the event (for direct invocation).
"""

from typing import Dict, Optional, Any


def read_session_key(event: Dict[str, Any]) -> Optional[str]:
    """
    Read the session key from the Lambda event (direct invocation only).

    Args:
        event: Lambda event object containing the input data

    Returns:
        str: The session key if found, None otherwise
    """
    if not isinstance(event, dict):
        return None

    # Direct invocation - extract sessionKey from event
    session_key = event.get("sessionKey")
    return session_key
