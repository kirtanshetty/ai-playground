"""
Game state management for 21 questions game.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, asdict


@dataclass
class GameState:
    """
    Represents the state of a 21 questions game session.
    """

    session_key: str
    questions_and_answers: List[Dict[str, str]]
    current_question_number: int
    target_person: Optional[str] = None
    game_completed: bool = False

    def to_dict(self) -> dict:
        """Convert GameState to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "GameState":
        """Create GameState from dictionary."""
        return cls(**data)

    def add_question_answer(self, question: str, answer: str):
        """Add a question and answer pair to the game state."""
        self.questions_and_answers.append({"question": question, "answer": answer})
        self.current_question_number += 1

    def get_question_count(self) -> int:
        """Get the number of questions asked so far."""
        return len(self.questions_and_answers)


def get_game_state(session_key: str, storage_backend=None) -> Optional[GameState]:
    """
    Retrieve game state for a given session key.

    Args:
        session_key: The session key to retrieve state for
        storage_backend: Optional storage backend (e.g., DynamoDB, S3, in-memory)
                        If None, uses in-memory storage (for development)

    Returns:
        GameState if found, None otherwise
    """
    if storage_backend is None:
        # In-memory storage for development/testing
        # In production, this would use DynamoDB or another persistent store
        return _in_memory_storage.get(session_key)

    return storage_backend.get(session_key)


def save_game_state(game_state: GameState, storage_backend=None):
    """
    Save game state for a session.

    Args:
        game_state: The GameState object to save
        storage_backend: Optional storage backend (e.g., DynamoDB, S3, in-memory)
                        If None, uses in-memory storage (for development)
    """
    if storage_backend is None:
        # In-memory storage for development/testing
        # In production, this would use DynamoDB or another persistent store
        _in_memory_storage[game_state.session_key] = game_state
        return

    storage_backend.save(game_state)


# In-memory storage for development/testing
# In production, replace this with DynamoDB or another persistent storage
_in_memory_storage: Dict[str, GameState] = {}
