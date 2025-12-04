"""
Node that uses the OpenAI client to call the LLM for the next question.
"""

import os
import json
from typing import Optional, Dict, Any

from llm import OpenAIClient


def get_next_question_from_prompt(
    prompt: str,
    model: str = "gpt-4",
    api_key: Optional[str] = None,
    **kwargs,
) -> str:
    """
    Use the OpenAI client to get the next question for the 21 questions game,
    given a fully constructed prompt.
    """
    # Initialize the OpenAI client
    client = OpenAIClient(api_key=api_key)

    # Call the LLM
    response = client.call(
        prompt=prompt,
        model=model,
        temperature=0.7,
        max_tokens=200,
        **kwargs,
    )

    # Extract the question from the response
    question = response.choices[0].message.content.strip()

    return question


def llm_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node that calls the LLM to get the next question.
    
    Args:
        state: State dictionary containing:
            - flow_state: Dictionary containing the prompt
            
    Returns:
        Updated state dictionary with:
            - next_question: The next question string from LLM
    """
    flow_state = state.get("flow_state") or {}
    prompt = flow_state.get("prompt")
    
    if not prompt:
        raise ValueError("prompt is required in flow_state")
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    # Parse API key if it's stored as JSON in Secrets Manager
    # Secrets Manager might store it as JSON: {"api_key": "sk-..."} or just the string
    if api_key:
        # Store original for fallback
        original_api_key = api_key
        # Check if it looks like JSON
        api_key = api_key.strip()
        if api_key.startswith("{") and api_key.endswith("}"):
            try:
                api_key_dict = json.loads(api_key)
                # Try common JSON key names for API key
                if isinstance(api_key_dict, dict):
                    # Try various possible key names, prioritizing common ones
                    extracted_key = (
                        api_key_dict.get("api_key") 
                        or api_key_dict.get("OPENAI_API_KEY") 
                        or api_key_dict.get("key")
                        or api_key_dict.get("value")
                        or (list(api_key_dict.values())[0] if api_key_dict else None)
                    )
                    # Only use extracted key if it's a valid string
                    if extracted_key and isinstance(extracted_key, str):
                        api_key = extracted_key
                    else:
                        # Fall back to original (might be plain string despite JSON format)
                        api_key = original_api_key
                else:
                    api_key = original_api_key
            except (json.JSONDecodeError, ValueError, IndexError):
                # If parsing fails, use the original value
                api_key = original_api_key
    
    # Call the LLM with the prompt
    next_question = get_next_question_from_prompt(
        prompt=prompt,
        model="gpt-4",
        api_key=api_key,
    )
    
    return {
        **state,
        # Values that need to be shared with later nodes stay on the main state
        "next_question": next_question,
    }
