"""
LangChain chain for the 21 questions game.
"""

import os
import sys
from typing import Dict, Any

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from langchain_core.runnables import RunnableLambda

from langchain.nodes.input_node import process_input_node
from langchain.nodes.db_node import load_game_state_node, save_game_state_node
from langchain.nodes.state_node import process_answer_node, update_state_with_question_node
from langchain.nodes.prompt_node import prompt_node
from langchain.nodes.llm_node import llm_node
from langchain.nodes.response_node import format_response_node


def create_twenty_one_questions_chain():
    """
    Create the LangChain chain for the 21 questions game.
    
    Returns:
        RunnableLambda: The compiled chain
    """
    # Build the chain by piping nodes together
    chain = (
        RunnableLambda(process_input_node)
        | RunnableLambda(load_game_state_node)
        | RunnableLambda(process_answer_node)
        | RunnableLambda(prompt_node)
        | RunnableLambda(llm_node)
        | RunnableLambda(update_state_with_question_node)
        | RunnableLambda(save_game_state_node)
        | RunnableLambda(format_response_node)
    )
    
    return chain


# Create the chain instance
twenty_one_questions_chain = create_twenty_one_questions_chain()

