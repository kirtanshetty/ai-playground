"""
Node that uses the OpenAI client to call the LLM for the next question.
"""

import os
import json
import re
from typing import Optional, Dict, Any, Tuple

from llm import OpenAIClient


def detect_guess(text: str) -> Tuple[bool, Optional[str]]:
    """
    Detect if the LLM response is a guess (not a question).
    A guess must:
    1. Be a question (contain ?)
    2. Ask about a specific person's name
    3. Match specific guess patterns like "Is it [Name]?" or "Are you thinking of [Name]?"
    4. The extracted name must look like a real person's name (not a phrase or description)
    
    Args:
        text: The LLM response text
        
    Returns:
        Tuple of (is_guess, guessed_person_name)
        - is_guess: True if the response appears to be a guess
        - guessed_person_name: The name of the person if it's a guess, None otherwise
    """
    text = text.strip()
    text_lower = text.lower()
    
    # Must contain a question mark to be a guess
    if '?' not in text:
        return False, None
    
    # Patterns that indicate a guess - more flexible, don't require exact start/end
    # Each pattern captures a person's name after a guess phrase
    # Allow for some text before/after (LLM might add context)
    guess_patterns = [
        r"is it (.+?)\?",  # "Is it Albert Einstein?"
        r"are you thinking of (.+?)\?",  # "Are you thinking of Albert Einstein?"
        r"could it be (.+?)\?",  # "Could it be Albert Einstein?"
        r"is (.+?) the person\?",  # "Is Albert Einstein the person?"
        r"my guess is (.+?)\?",  # "My guess is Albert Einstein?"
        r"i think it's (.+?)\?",  # "I think it's Albert Einstein?"
        r"i believe it's (.+?)\?",  # "I believe it's Albert Einstein?"
        r"are you (.+?)\?",  # "Are you Albert Einstein?"
        r"is the person you're thinking of (.+?)\?",  # "Is the person you're thinking of Albert Einstein?"
        # Note: "Is the person [X]?" is NOT a guess pattern - it's a regular question format
        # So we don't include it here
    ]
    
    for pattern in guess_patterns:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            guessed_name = match.group(1).strip()
            # Clean up the name (remove quotes, extra spaces, trailing punctuation)
            guessed_name = re.sub(r'^["\']|["\']$', '', guessed_name).strip()
            guessed_name = re.sub(r'[.,;:!?]+$', '', guessed_name).strip()
            
            # Validate that it looks like a person's name
            if guessed_name and is_valid_person_name(guessed_name):
                # Capitalize the name properly (first letter of each word)
                guessed_name = ' '.join(word.capitalize() for word in guessed_name.split())
                return True, guessed_name
    
    return False, None


def is_valid_person_name(name: str) -> bool:
    """
    Validate if a string looks like a real person's name.
    More lenient - allows lowercase names and focuses on excluding invalid phrases.
    
    Args:
        name: The string to validate
        
    Returns:
        True if it looks like a person's name, False otherwise
    """
    if not name or len(name) < 2:
        return False
    
    # Split into words
    words = name.split()
    
    # Person names are usually 1-4 words (allow up to 5 for names like "Mary Jane Watson")
    if len(words) > 5:
        return False
    
    # Exclude common phrases that aren't names
    invalid_phrases = [
        'trying to', 'identify', 'a male', 'a female', 'male', 'female',
        'person', 'someone', 'somebody', 'anyone', 'anybody',
        'real person', 'famous person', 'historical figure',
        'yes', 'no', 'maybe', 'perhaps', 'possibly',
        'thinking of', 'you are', 'you\'re', 'i am', 'i\'m',
        'the person', 'this person', 'that person',
        # Common adjectives/descriptive words that aren't names
        'alive', 'dead', 'famous', 'unknown', 'young', 'old', 'tall', 'short',
        'rich', 'poor', 'smart', 'famous', 'popular', 'well-known',
    ]
    
    name_lower = name.lower().strip()
    
    # Check for invalid phrases
    for phrase in invalid_phrases:
        if phrase in name_lower:
            return False
    
    # Exclude if it's just a description (starts with "a" or "an" followed by adjective)
    if re.match(r'^(a|an|the)\s+[a-z]+', name_lower):
        return False
    
    # Exclude if it contains question words (unless it's part of a compound name, which is rare)
    question_words = ['what', 'where', 'when', 'why', 'how', 'which']
    for word in question_words:
        if word in name_lower.split():  # Only check if it's a whole word
            return False
    
    # Exclude if it's too generic (single common words that aren't names)
    generic_words = ['who', 'someone', 'anyone', 'somebody', 'anybody', 'person']
    if name_lower in generic_words:
        return False
    
    # Exclude if it looks like a sentence or contains verbs
    # Common verbs that shouldn't be in names
    verbs = ['is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had']
    if any(verb in name_lower.split() for verb in verbs):
        return False
    
    # If we've passed all the exclusion checks, it's likely a name
    # (even if lowercase, we'll capitalize it later)
    return True


def get_next_question_from_prompt(
    prompt: str,
    model: str = "gpt-4",
    api_key: Optional[str] = None,
    **kwargs,
) -> Tuple[str, bool, Optional[str]]:
    """
    Use the OpenAI client to get the next question for the 21 questions game,
    given a fully constructed prompt.
    
    Returns:
        Tuple of (response_text, is_guess, guessed_person_name)
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

    # Extract the response from the LLM
    response_text = response.choices[0].message.content.strip()
    
    # Check if LLM explicitly included "guess:true" in the response
    has_guess_flag = "guess:true" in response_text.lower()
    
    # Remove "guess:true" from the response text if present (clean it up)
    if has_guess_flag:
        response_text = re.sub(r'\s*guess:\s*true\s*', '', response_text, flags=re.IGNORECASE).strip()
    
    # Detect if it's a guess (either via pattern matching or explicit flag)
    is_guess, guessed_person = detect_guess(response_text)
    
    # If LLM explicitly said "guess:true", treat it as a guess even if pattern doesn't match
    if has_guess_flag and not is_guess:
        is_guess = True
        # Try to extract person name from the question if we can
        if not guessed_person:
            # Try to extract from common guess patterns
            for pattern in [r"is it (.+?)\?", r"are you thinking of (.+?)\?", r"are you (.+?)\?"]:
                match = re.search(pattern, response_text.lower(), re.IGNORECASE)
                if match:
                    guessed_person = match.group(1).strip()
                    guessed_person = re.sub(r'^["\']|["\']$', '', guessed_person).strip()
                    guessed_person = ' '.join(word.capitalize() for word in guessed_person.split())
                    break
    
    return response_text, is_guess, guessed_person


def llm_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node that calls the LLM to get the next question.
    Skips LLM call if prompt is None (game completed).
    
    Args:
        state: State dictionary containing:
            - flow_state: Dictionary containing the prompt
            
    Returns:
        Updated state dictionary with:
            - next_question: The next question string from LLM (or None if game completed)
            - is_guess: Boolean indicating if response is a guess
            - guessed_person: Name of person if it's a guess
    """
    flow_state = state.get("flow_state") or {}
    prompt = flow_state.get("prompt")
    
    # If prompt is None, game is completed - skip LLM call
    if prompt is None:
        return {
            **state,
            "next_question": None,
            "is_guess": False,
            "guessed_person": None,
        }
    
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
    response_text, is_guess, guessed_person = get_next_question_from_prompt(
        prompt=prompt,
        model="gpt-4",
        api_key=api_key,
    )
    
    return {
        **state,
        # Values that need to be shared with later nodes stay on the main state
        "next_question": response_text,
        "is_guess": is_guess,
        "guessed_person": guessed_person,
    }
