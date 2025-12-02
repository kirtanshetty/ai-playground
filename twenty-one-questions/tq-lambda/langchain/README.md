# Langchain Module for 21 Questions Game

This folder contains nodes and chains for the 21 questions game to identify a person.

## Structure

- **`nodes/`**: Contains individual nodes
  - **`session_node.py`**: Node that reads the session key from the Lambda event
  - **`prompt_node.py`**: Node that creates a prompt for the 21 questions game
  - **`llm_node.py`**: Node that uses the OpenAI client to get the next question
- **`chains/`**: Contains chain definitions (for future use)
- **`states/`**: Contains state management
  - **`game_state.py`**: GameState class and state management functions

## Usage

```python
from langchain import read_session_key, create_21_questions_prompt, get_next_question

# Read session key from event
session_key = read_session_key(event)

# Create prompt with previous questions and answers
questions_and_answers = [
    {"question": "Are you a real person?", "answer": "Yes"},
    {"question": "Are you alive today?", "answer": "No"}
]
prompt = create_21_questions_prompt(questions_and_answers, current_question_number=3)

# Get the next question from LLM
next_question = get_next_question(
    questions_and_answers=questions_and_answers,
    current_question_number=3,
    model="gpt-4"
)
```

## Nodes

### read_session_key(event)

Extracts the session key from various Lambda event formats:
- POST requests with JSON body
- GET requests with query parameters
- Direct Lambda invocations

### create_21_questions_prompt(questions_and_answers, current_question_number)

Creates a formatted prompt for the 21 questions game. Includes:
- Game rules and instructions
- Previous questions and answers (if any)
- Request for the next question

### get_next_question(questions_and_answers, current_question_number, model, api_key, **kwargs)

Calls the OpenAI API to generate the next question. Uses the prompt node internally and returns the generated question as a string.

## States

### GameState

Represents the state of a 21 questions game session.

**Attributes:**
- `session_key`: Unique identifier for the game session
- `questions_and_answers`: List of previous Q&A pairs
- `current_question_number`: Current question number (1-21)
- `target_person`: The person being identified (optional, set when game completes)
- `game_completed`: Whether the game has been completed

**Methods:**
- `add_question_answer(question, answer)`: Add a new Q&A pair
- `get_question_count()`: Get the number of questions asked
- `to_dict()`: Convert to dictionary
- `from_dict(data)`: Create from dictionary

### get_game_state(session_key, storage_backend=None)

Retrieve game state for a given session key.

### save_game_state(game_state, storage_backend=None)

Save game state for a session.

**Example:**
```python
from langchain.states import GameState, get_game_state, save_game_state

# Get existing state or create new
game_state = get_game_state(session_key)
if not game_state:
    game_state = GameState(
        session_key=session_key,
        questions_and_answers=[],
        current_question_number=1
    )

# Add a question and answer
game_state.add_question_answer("Are you a real person?", "Yes")

# Save the state
save_game_state(game_state)
```

