"""
LLM node - calls OpenAI to get the next question.
"""

import os
import json
import re
from typing import Dict, Any, Tuple, Optional

from llm import OpenAIClient


def parse_llm_response(response_text: str) -> Tuple[str, bool]:
    """
    Parse JSON response from LLM.
    
    Returns:
        Tuple of (question, guessingPersonality)
    """
    response_text = response_text.strip()
    
    # Find JSON in response
    json_match = re.search(r'\{[^{}]*\}', response_text, re.DOTALL)
    
    if json_match:
        try:
            data = json.loads(json_match.group(0))
            question = data.get("question", "").strip()
            guessing = data.get("guessingPersonality", False)
            
            if isinstance(guessing, str):
                guessing = guessing.lower() == "true"
            
            if question:
                return question, bool(guessing)
        except json.JSONDecodeError:
            pass
    
    # Fallback: use raw text as question, assume not guessing
    clean_text = re.sub(r'[{}"\n]', '', response_text).strip()
    clean_text = re.sub(r'question:\s*', '', clean_text, flags=re.IGNORECASE)
    clean_text = re.sub(r'guessingPersonality:\s*(true|false)', '', clean_text, flags=re.IGNORECASE)
    return clean_text.strip(), False


def extract_person_name(question: str) -> Optional[str]:
    """
    Extract person name from a guess question like "Is it Elon Musk?"
    """
    patterns = [
        r"is it (.+?)\?",
        r"are you thinking of (.+?)\?",
        r"is the person (.+?)\?",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, question, re.IGNORECASE)
        if match:
            name = match.group(1).strip()
            name = re.sub(r'^["\']|["\']$', '', name)
            if name and len(name) > 1:
                # Capitalize each word
                return ' '.join(word.capitalize() for word in name.split())
    
    return None


def get_api_key() -> Optional[str]:
    """Get OpenAI API key from environment."""
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        return None
    
    api_key = api_key.strip()
    
    # Handle JSON-wrapped key from Secrets Manager
    if api_key.startswith("{"):
        try:
            data = json.loads(api_key)
            if isinstance(data, dict):
                return (
                    data.get("api_key") or 
                    data.get("OPENAI_API_KEY") or 
                    data.get("key") or
                    list(data.values())[0] if data else None
                )
        except (json.JSONDecodeError, IndexError):
            pass
    
    return api_key


def llm_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call LLM to get next question.
    
    Input state:
        - flow_state.prompt: The prompt to send to LLM
        
    Output state:
        - next_question: The question text
        - guessing_personality: Boolean - is this a guess?
        - guessed_person: Person name if guessing
    """
    flow_state = state.get("flow_state") or {}
    prompt = flow_state.get("prompt")
    
    # Skip if no prompt (game completed)
    if not prompt:
        return {
            **state,
            "next_question": None,
            "guessing_personality": False,
            "guessed_person": None,
        }
    
    # Call LLM
    api_key = get_api_key()
    client = OpenAIClient(api_key=api_key)
    
    response = client.call(
        prompt=prompt,
        model="gpt-4",
        temperature=0.7,
        max_tokens=150,
    )
    
    response_text = response.choices[0].message.content.strip()
    
    # Parse response
    question, guessing_personality = parse_llm_response(response_text)
    
    # Extract person name if guessing
    guessed_person = None
    if guessing_personality:
        guessed_person = extract_person_name(question)
    
    return {
        **state,
        "next_question": question,
        "guessing_personality": guessing_personality,
        "guessed_person": guessed_person,
    }
