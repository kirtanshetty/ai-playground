"""
LangChain prompt class for 21 questions game.
"""

from typing import List, Dict, Optional
from langchain.prompts import PromptTemplate


class TwentyOneQuestionsPrompt:
    """
    LangChain prompt class for generating prompts for the 21 questions game.
    """

    def __init__(self):
        """Initialize the prompt class with the template."""
        # Read the prompt template from the text file
        import os

        prompt_file = os.path.join(os.path.dirname(__file__), "prompt_template.txt")
        with open(prompt_file, "r") as f:
            template = f.read()

        self.prompt_template = PromptTemplate(
            input_variables=["questions_and_answers", "current_question_number"],
            template=template,
        )

    def generate_prompt(
        self,
        questions_and_answers: Optional[List[Dict[str, str]]] = None,
        current_question_number: int = 1,
    ) -> PromptTemplate:
        """
        Generate a LangChain prompt object for the 21 questions game.

        Args:
            questions_and_answers: List of previous Q&A pairs. Each dict should have:
                - 'question': The question asked
                - 'answer': The answer given
            current_question_number: The current question number (1-21)

        Returns:
            PromptTemplate: The formatted LangChain prompt object with the prompt text
        """
        # Format questions and answers as a string
        if questions_and_answers and len(questions_and_answers) > 0:
            qa_lines = []
            qa_lines.append("Here are the questions asked so far and their answers:\n")
            for i, qa in enumerate(questions_and_answers, 1):
                question = qa.get("question", "")
                answer = qa.get("answer", "")
                qa_lines.append(f"Question {i}: {question}")
                qa_lines.append(f"Answer: {answer}\n")
            qa_text = "\n".join(qa_lines)
        else:
            qa_text = "No questions asked yet.\n"

        # Format the prompt with the template
        formatted_prompt = self.prompt_template.format(
            questions_and_answers=qa_text,
            current_question_number=current_question_number,
        )

        # Return a new PromptTemplate with the formatted text
        return PromptTemplate(input_variables=[], template=formatted_prompt)

    def get_prompt_template(self) -> PromptTemplate:
        """
        Get the base prompt template.

        Returns:
            PromptTemplate: The base prompt template
        """
        return self.prompt_template
