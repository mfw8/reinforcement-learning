# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Explainable Reinforcement Learning Othello (Reversi) game built with Python, Pygame, and Stable-Baselines3. It combines human gameplay with AI opponents and provides real-time AI analysis using local Ollama LLM for explainability.

## Running the Application

```bash
python main.py
```

The game presents 4 modes:
1. Human vs Human
2. Human vs Random AI
3. Human vs Trained AI (loads `othello_ppo.zip`)
4. Train an AI now (default: 20,000 timesteps)

## Architecture

### Core Game Flow (main.py)
- `main()` handles mode selection, game loop, event handling, and AI move execution
- Game state is represented as 8x8 numpy array: `1` = Black, `-1` = White, `0` = Empty
- Move history tracking enables undo functionality with analysis

### Module Responsibilities

**logic.py** - Core Othello game rules
- `init_board()`: Creates starting 8x8 board with center pieces
- `is_valid_move()`, `get_valid_moves()`: Move validation using 8-directional scanning
- `place_disc()`: Places disc and flips opponent pieces in all valid directions
- `has_valid_moves()`, `count_discs()`: Game state queries

**env.py** - Gymnasium environment wrapper
- `OthelloGymEnv`: Gym-compatible environment for RL training
- Observation space: 8x8 array of {-1, 0, 1}
- Action space: Discrete(64) representing board positions
- Reward structure: -0.1 for invalid moves, +1.04/-1.0/0.0 for win/loss/tie at terminal state

**ai.py** - Reinforcement learning training
- `train_agent()`: Trains PPO model using Stable-Baselines3
- `load_model()`: Loads pre-trained model from `MODEL_PATH` (defaults to "othello_ppo.zip")
- Uses `DummyVecEnv` wrapper with MlpPolicy

**explainability_local.py** - AI-powered game analysis
- Uses local Ollama with `llama3.2:1b` model for free, offline analysis
- `check_ollama()`: Verifies Ollama service is running on localhost:11434
- `get_board_analysis()`: Analyzes current position and suggests best moves
- `get_game_summary()`: Post-game analysis with strategic insights
- `get_move_explanation()`: Explains specific move quality
- All prompts emphasize Othello terminology to avoid chess confusion

**heatmap.py** - Move quality visualization
- `calculate_heuristic_scores()`: Scores moves using position values, disc flipping, and mobility
- Position matrix: Corners (100), edges (10), center (1-5), X-squares (-40), C-squares (-20)
- `generate_heatmap_surface()`: Creates cached pygame surface with color-coded move scores (red=bad, yellow=medium, green=good)
- Heatmap generation is expensive; surface is cached per board state hash

**undo.py** - Move history and retrospective analysis
- `MoveHistory`: Stack-based move tracker storing (board_state, player, row, col)
- `analyze_move_quality()`: Heuristic-based move analysis covering position type, disc count, mobility, corner access
- `analyze_move_with_ai()`: Uses Ollama to explain why an undone move was good/bad
- Strategic insights emphasize Othello principles: corners > edges > center, mobility control, avoiding X-squares

**ui.py** - Pygame rendering
- `draw_board()`: Renders 8x8 grid with pieces, valid move highlights, and score display
- `show_analysis()`: Scrollable text overlay for AI analysis (supports arrow keys, PageUp/Down, mouse scroll)
- `end_screen()`: Game over screen with win tracking across sessions

**constants.py** - Configuration
- Board: 8x8 grid, 80px cells, 640x700 window (60px bottom panel)
- Model path, colors, FPS settings
- `total_scores` tracks wins across multiple games in a session

## Interactive Features

**Keyboard Controls (Human vs Human / Human vs Random AI)**
- `H`: Request AI analysis of current board position
- `M`: Toggle move heatmap showing strategic value of each valid move
- `U`: Undo last move and receive AI explanation of why it was made
- `C`: Continue to new game after game over
- `Q`/`ESC`: Quit or close analysis overlay

**Mouse Controls**
- Click valid squares to place discs (highlights shown in yellow)

## Dependencies

Key libraries:
- `pygame`: Game rendering and event handling
- `numpy`: Board state representation and calculations
- `gymnasium`: RL environment interface (formerly gym)
- `stable-baselines3`: PPO reinforcement learning
- `requests`: Ollama API communication

Install Ollama for AI analysis:
1. Download from https://ollama.com
2. Run `ollama pull llama3.2:1b` to get the 1.3GB model
3. Ollama service auto-starts on port 11434

## Development Patterns

### Board State Representation
- Player values: Black=1, White=-1, Empty=0
- Current player flips each turn: `current_player *= -1`
- Pass rule: If no valid moves, turn passes back to opponent

### Move Validation
- 8-directional search: `[(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]`
- Valid move must flip ≥1 opponent disc in any direction
- Flipping requires opponent discs sandwiched between player discs

### Caching Strategy
- Heatmap surface cached with board hash to avoid expensive recalculation
- Cleared on move execution or undo
- Generated once per board state, toggled on/off with 'M' key

### AI Move Selection (Trained Agent)
- Predict action from board observation: `action, _ = model.predict(obs, deterministic=True)`
- Convert action index to (row, col): `divmod(int(action), BOARD_SIZE)`
- Fallback to random valid move if predicted action is invalid

### Explainability Design
- Prompts explicitly request Othello terminology (discs, flip, corners, edges)
- Emphasizes avoiding chess terms (king, queen, checkmate)
- Temperature 0.7 for balanced creativity/consistency
- Response limited to 200-400 tokens for speed
- 2-minute timeout for all AI requests

## Training Notes

- Default training: 20,000 timesteps with PPO
- Model saved to `othello_ppo.zip` after training
- Black player perspective: reward +1.04 for win, -1.0 for loss
- Invalid moves penalized -0.1 during training
- Sparse rewards (only at game end) make learning challenging
