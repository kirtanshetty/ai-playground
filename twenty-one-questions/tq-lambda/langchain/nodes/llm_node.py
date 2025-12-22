"""
Node that uses the OpenAI client to call the LLM for the next question.
"""

import os
import json
import re
from typing import Optional, Dict, Any, Tuple

from llm import OpenAIClient


def parse_llm_json_response(response_text: str) -> Tuple[str, bool]:
    """
    Parse the JSON response from the LLM.
    
    Args:
        response_text: The raw response text from the LLM
        
    Returns:
        Tuple of (question, guessingPersonality)
    """
    response_text = response_text.strip()
    
    # Try to extract JSON from the response
    # Sometimes LLM might include extra text before/after the JSON
    json_match = re.search(r'\{[^{}]*\}', response_text, re.DOTALL)
    
    if json_match:
        try:
            json_str = json_match.group(0)
            data = json.loads(json_str)
            
            question = data.get("question", "").strip()
            guessing_personality = data.get("guessingPersonality", False)
            
            # Ensure guessingPersonality is a boolean
            if isinstance(guessing_personality, str):
                guessing_personality = guessing_personality.lower() == "true"
            
            if question:
                return question, bool(guessing_personality)
        except (json.JSONDecodeError, ValueError):
            pass
    
    # Fallback: If JSON parsing fails, try to extract question and detect if it's a guess
    # This handles cases where LLM doesn't follow the JSON format
    question = response_text
    
    # Remove any JSON-like artifacts
    question = re.sub(r'[{}":]', '', question).strip()
    question = re.sub(r'\s*(question|guessingPersonality)\s*', '', question, flags=re.IGNORECASE).strip()
    question = re.sub(r'\s*(true|false)\s*$', '', question, flags=re.IGNORECASE).strip()
    
    # Detect if it's a guess based on patterns
    guessing_personality = detect_guess_from_question(question)
    
    return question, guessing_personality


def detect_guess_from_question(question: str) -> bool:
    """
    Detect if a question is a guess about a specific person.
    
    Args:
        question: The question text
        
    Returns:
        True if the question appears to be a guess about a specific person
    """
    question_lower = question.lower().strip()
    
    # Patterns that indicate a guess about a specific person
    guess_patterns = [
        r"is it (.+?)\?",  # "Is it Albert Einstein?"
        r"are you thinking of (.+?)\?",  # "Are you thinking of Albert Einstein?"
        r"could it be (.+?)\?",  # "Could it be Albert Einstein?"
        r"is (.+?) the person\?",  # "Is Albert Einstein the person?"
        r"my guess is (.+?)\?",  # "My guess is Albert Einstein?"
        r"i think it's (.+?)\?",  # "I think it's Albert Einstein?"
        r"i believe it's (.+?)\?",  # "I believe it's Albert Einstein?"
        r"are you (.+?)\?",  # "Are you Albert Einstein?"
        r"is the person you're thinking of (.+?)\?",  # Full pattern
    ]
    
    for pattern in guess_patterns:
        match = re.search(pattern, question_lower, re.IGNORECASE)
        if match:
            guessed_name = match.group(1).strip()
            # Validate it looks like a person's name (not a generic phrase)
            if guessed_name and is_valid_person_name(guessed_name):
                return True
    
    return False


def extract_guessed_person(question: str) -> Optional[str]:
    """
    Extract the person's name from a guess question.
    
    Args:
        question: The question text
        
    Returns:
        The guessed person's name, or None if not a guess
    """
    question_lower = question.lower().strip()
    
    guess_patterns = [
        r"is it (.+?)\?",
        r"are you thinking of (.+?)\?",
        r"could it be (.+?)\?",
        r"is (.+?) the person\?",
        r"my guess is (.+?)\?",
        r"i think it's (.+?)\?",
        r"i believe it's (.+?)\?",
        r"are you (.+?)\?",
        r"is the person you're thinking of (.+?)\?",
    ]
    
    for pattern in guess_patterns:
        match = re.search(pattern, question_lower, re.IGNORECASE)
        if match:
            guessed_name = match.group(1).strip()
            # Clean up the name
            guessed_name = re.sub(r'^["\']|["\']$', '', guessed_name).strip()
            guessed_name = re.sub(r'[.,;:!?]+$', '', guessed_name).strip()
            
            if guessed_name and is_valid_person_name(guessed_name):
                # Capitalize properly
                guessed_name = ' '.join(word.capitalize() for word in guessed_name.split())
                return guessed_name
    
    return None


def is_valid_person_name(name: str) -> bool:
    """
    Validate if a string looks like a real person's name.
    Must be strict to avoid false positives like "Involved In The Entertainment Industry".
    
    Args:
        name: The string to validate
        
    Returns:
        True if it looks like a person's name, False otherwise
    """
    if not name or len(name) < 2:
        return False
    
    name_lower = name.lower().strip()
    words = name_lower.split()
    
    # Person names are usually 1-4 words (First Last, or First Middle Last, etc.)
    if len(words) > 4:
        return False
    
    # Exclude common phrases and words that aren't names
    invalid_words = [
        # Articles and prepositions (names don't typically have these unless it's like "Leonardo da Vinci")
        'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'with', 'by', 'from', 'of',
        # Verbs
        'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
        'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
        'involved', 'known', 'born', 'died', 'worked', 'living', 'active',
        # Adjectives and descriptors
        'alive', 'dead', 'famous', 'unknown', 'young', 'old', 'rich', 'poor',
        'smart', 'popular', 'well-known', 'male', 'female', 'american', 'british',
        'entertainment', 'industry', 'music', 'film', 'movie', 'sports', 'politics',
        'science', 'business', 'technology', 'historical', 'modern', 'contemporary',
        # Pronouns and generic words
        'person', 'someone', 'somebody', 'anyone', 'anybody', 'they', 'them',
        'this', 'that', 'these', 'those', 'who', 'what', 'where', 'when', 'why', 'how',
        # Common non-name words
        'yes', 'no', 'maybe', 'perhaps', 'possibly', 'probably', 'definitely',
        'thinking', 'trying', 'identify', 'guess', 'figure',
    ]
    
    # Check if any word in the name is in the invalid list
    for word in words:
        if word in invalid_words:
            return False
    
    # Exclude if it looks like a phrase/sentence (more than 2 words and contains common words)
    if len(words) > 2:
        # Allow "da", "de", "van", "von" for names like "Leonardo da Vinci"
        allowed_connectors = ['da', 'de', 'van', 'von', 'del', 'la', 'le', 'al', 'bin', 'ibn']
        non_connector_words = [w for w in words if w not in allowed_connectors]
        # If after removing connectors we still have more than 3 words, it's likely not a name
        if len(non_connector_words) > 3:
            return False
    
    # Names should generally start with a capital letter (when properly formatted)
    # But since we're checking lowercase, we check if original had capitals
    original_words = name.strip().split()
    if len(original_words) > 0:
        # At least the first word should have started with a letter
        first_word = original_words[0]
        if not first_word[0].isalpha():
            return False
    
    # Exclude if it's a question or statement
    if '?' in name or name_lower.startswith(('is ', 'are ', 'was ', 'were ', 'do ', 'does ')):
        return False
    
    return True


def get_next_question_from_prompt(
    prompt: str,
    model: str = "gpt-4",
    api_key: Optional[str] = None,
    **kwargs,
) -> Tuple[str, bool, Optional[str]]:
    """
    Use the OpenAI client to get the next question for the 21 questions game.
    
    Returns:
        Tuple of (question, guessingPersonality, guessed_person_name)
    """
    client = OpenAIClient(api_key=api_key)

    response = client.call(
        prompt=prompt,
        model=model,
        temperature=0.7,
        max_tokens=200,
        **kwargs,
    )

    response_text = response.choices[0].message.content.strip()
    
    # Parse the JSON response
    question, guessing_personality = parse_llm_json_response(response_text)
    
    # Extract the guessed person's name if it's a guess
    guessed_person = None
    if guessing_personality:
        guessed_person = extract_guessed_person(question)
    
    return question, guessing_personality, guessed_person


def llm_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node that calls the LLM to get the next question.
    
    Args:
        state: State dictionary containing:
            - flow_state: Dictionary containing the prompt
            
    Returns:
        Updated state dictionary with:
            - next_question: The next question string from LLM
            - guessing_personality: Boolean indicating if this is a guess
            - guessed_person: Name of person if it's a guess
    """
    flow_state = state.get("flow_state") or {}
    prompt = flow_state.get("prompt")
    
    # If prompt is None, game is completed - skip LLM call
    if prompt is None:
        return {
            **state,
            "next_question": None,
            "guessing_personality": False,
            "guessed_person": None,
        }
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    # Parse API key if it's stored as JSON in Secrets Manager
    if api_key:
        original_api_key = api_key
        api_key = api_key.strip()
        if api_key.startswith("{") and api_key.endswith("}"):
            try:
                api_key_dict = json.loads(api_key)
                if isinstance(api_key_dict, dict):
                    extracted_key = (
                        api_key_dict.get("api_key") 
                        or api_key_dict.get("OPENAI_API_KEY") 
                        or api_key_dict.get("key")
                        or api_key_dict.get("value")
                        or (list(api_key_dict.values())[0] if api_key_dict else None)
                    )
                    if extracted_key and isinstance(extracted_key, str):
                        api_key = extracted_key
                    else:
                        api_key = original_api_key
                else:
                    api_key = original_api_key
            except (json.JSONDecodeError, ValueError, IndexError):
                api_key = original_api_key
    
    # Call the LLM with the prompt
    question, guessing_personality, guessed_person = get_next_question_from_prompt(
        prompt=prompt,
        model="gpt-4",
        api_key=api_key,
    )
    
    return {
        **state,
        "next_question": question,
        "guessing_personality": guessing_personality,
        "guessed_person": guessed_person,
    }
