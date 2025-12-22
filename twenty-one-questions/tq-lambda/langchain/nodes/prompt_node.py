"""
Prompt node - creates the prompt for the LLM.
"""

import os
from typing import Dict, Any

MAX_QUESTIONS = 21


def load_prompt_template() -> str:
    """Load the prompt template from file."""
    template_path = os.path.join(
        os.path.dirname(__file__), 
        "../prompt/prompt_template.txt"
    )
    with open(template_path, "r") as f:
        return f.read()


def format_qa_history(questions_and_answers: list) -> str:
    """Format Q&A history for the prompt."""
    if not questions_and_answers:
        return "No questions asked yet.\n"
    
    lines = ["Previous questions and answers:\n"]
    for i, qa in enumerate(questions_and_answers, 1):
        question = qa.get("question", "")
        answer = qa.get("answer", "")
        guessing = qa.get("guessingPersonality", False)
        
        # Show whether it was a guess
        guess_marker = " [GUESS]" if guessing else ""
        lines.append(f"Q{i}{guess_marker}: {question}")
        lines.append(f"A{i}: {answer}\n")
    
    return "\n".join(lines)


def prompt_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create prompt for LLM.
    
    Sets flow_state.prompt to None if game is already over.
    """
    game_state = state.get("game_state")
    
    if not game_state:
        raise ValueError("game_state is required")
    
    flow_state = dict(state.get("flow_state") or {})
    
    # Don't create prompt if game is over
    if game_state.game_completed:
        flow_state["prompt"] = None
        return {**state, "flow_state": flow_state}
    
    # Load template and format
    template = load_prompt_template()
    qa_history = format_qa_history(game_state.questions_and_answers)
    
    prompt = template.format(
        questions_and_answers=qa_history,
        current_question_number=game_state.current_question_number,
    )
    
    flow_state["prompt"] = prompt
    
    return {**state, "flow_state": flow_state}
