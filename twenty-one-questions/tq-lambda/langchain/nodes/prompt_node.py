"""
Node that creates a prompt for the 21 questions game to identify a person.
"""

from typing import List, Dict, Optional


def create_21_questions_prompt(
    questions_and_answers: Optional[List[Dict[str, str]]] = None,
    current_question_number: int = 1,
) -> str:
    """
    Create a prompt for the 21 questions game to identify a person.

    Args:
        questions_and_answers: List of previous Q&A pairs. Each dict should have:
            - 'question': The question asked
            - 'answer': The answer given
        current_question_number: The current question number (1-21)

    Returns:
        str: The formatted prompt for the LLM
    """
    base_prompt = """You are playing a game of "21 Questions to Identify the Person".
The goal is to identify a famous person (real or fictional) by asking up to 21 yes/no questions.

Rules:
- You can only ask yes/no questions
- You have up to 21 questions total
- Try to narrow down the possibilities with each question
- Be strategic and ask questions that eliminate many possibilities at once
- Once you're confident, you can make a guess about who the person is

"""

    if questions_and_answers and len(questions_and_answers) > 0:
        prompt = base_prompt + "Here are the questions asked so far and their answers:\n\n"

        for i, qa in enumerate(questions_and_answers, 1):
            question = qa.get("question", "")
            answer = qa.get("answer", "")
            prompt += f"Question {i}: {question}\n"
            prompt += f"Answer: {answer}\n\n"

        prompt += (
            f"Based on the information above, ask question "
            f"{current_question_number} to help identify the person.\n"
        )
        prompt += (
            "Only ask one yes/no question. "
            "Do not make a guess yet unless you are very confident."
        )
    else:
        prompt = (
            base_prompt
            + f"Ask question {current_question_number} to start identifying the person.\n"
        )
        prompt += "Only ask one yes/no question."

    return prompt
