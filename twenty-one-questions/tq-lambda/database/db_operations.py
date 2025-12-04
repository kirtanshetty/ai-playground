"""
Database operations for managing game state in RDS.
"""

import json
from typing import Optional
from langchain.states.game_state import GameState


def initialize_database_table(db_client):
    """
    Initialize the ai_playground table if it doesn't exist.
    
    Args:
        db_client: Database client instance
    """
    create_table_query = """
    CREATE TABLE IF NOT EXISTS ai_playground (
        session_key VARCHAR(255) PRIMARY KEY,
        email VARCHAR(255),
        tq_state TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    try:
        db_client.execute_update(create_table_query)
    except Exception as e:
        # Table might already exist, or there's a connection issue
        print(f"Note: Could not create table (may already exist): {str(e)}")


def get_game_state_from_db(db_client, session_key: str) -> Optional[GameState]:
    """
    Retrieve game state from database for a given session key.
    
    Args:
        db_client: Database client instance
        session_key: The session key to retrieve state for
        
    Returns:
        GameState if found, None otherwise
    """
    query = "SELECT email, tq_state FROM ai_playground WHERE session_key = %s"
    results = db_client.execute_query(query, (session_key,))
    
    if not results or len(results) == 0:
        return None
    
    row = results[0]
    email = row[0]
    tq_state_json = row[1]
    
    if not tq_state_json:
        return None
    
    try:
        state_data = json.loads(tq_state_json)
        return GameState.from_dict(state_data)
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"Error parsing game state: {str(e)}")
        return None


def save_game_state_to_db(db_client, game_state: GameState, email: Optional[str] = None):
    """
    Save game state to database.
    
    Args:
        db_client: Database client instance
        game_state: The GameState object to save
        email: Optional email address
    """
    tq_state_json = json.dumps(game_state.to_dict())
    
    # Use UPSERT (INSERT ... ON CONFLICT UPDATE)
    query = """
    INSERT INTO ai_playground (session_key, email, tq_state, updated_at)
    VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
    ON CONFLICT (session_key)
    DO UPDATE SET
        email = EXCLUDED.email,
        tq_state = EXCLUDED.tq_state,
        updated_at = CURRENT_TIMESTAMP
    """
    
    db_client.execute_update(query, (game_state.session_key, email, tq_state_json))

