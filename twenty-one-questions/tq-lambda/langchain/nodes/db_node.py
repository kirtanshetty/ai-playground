"""
Node for database operations - loading and saving game state.
"""

import sys
import os
from typing import Dict, Any, Optional

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from database.db_client import get_db_client
from database.db_operations import (
    initialize_database_table,
    get_game_state_from_db,
    save_game_state_to_db,
)
from langchain.states.game_state import GameState


def load_game_state_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Load game state from database or initialize new state.
    
    Args:
        state: State dictionary containing:
            - session_key: Session key to load state for
            - email: Optional email address
            
    Returns:
        Updated state dictionary with:
            - game_state: GameState object (new or loaded from DB)
            - db_client: Database client instance
    """
    session_key = state.get("session_key")
    email = state.get("email")
    
    if not session_key:
        raise ValueError("session_key is required in state")
    
    # Initialize database client and table
    db_client = get_db_client()
    initialize_database_table(db_client)
    
    # Load existing game state or initialize new one
    game_state = get_game_state_from_db(db_client, session_key)
    
    if game_state is None:
        # Initialize new game state
        game_state = GameState(
            session_key=session_key,
            questions_and_answers=[],
            current_question_number=1,
        )
    
    return {
        **state,
        "game_state": game_state,
        "db_client": db_client,
    }


def save_game_state_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Save game state to database.
    
    Args:
        state: State dictionary containing:
            - game_state: GameState object to save
            - db_client: Database client instance
            - email: Optional email address
            
    Returns:
        Updated state dictionary
    """
    game_state = state.get("game_state")
    db_client = state.get("db_client")
    email = state.get("email")
    
    if not game_state:
        raise ValueError("game_state is required in state")
    if not db_client:
        raise ValueError("db_client is required in state")
    
    save_game_state_to_db(db_client, game_state, email)
    
    return state

