import requests
import json
from logic import count_discs, get_valid_moves
from constants import BOARD_SIZE

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:1b"  # Much faster, smaller model
TIMEOUT = 120  # 2 minutes timeout

def check_ollama():
    """Check if Ollama is running locally."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            print("✅ Ollama is running!")
            return True
    except:
        pass
    
    print("❌ Ollama not found!")
    print("\n📦 To use free local AI analysis:")
    print("  1. Download Ollama from: https://ollama.com")
    print("  2. Install and run it")
    print("  3. In a terminal, run: ollama pull llama3.2:1b")
    print("  4. Ollama will start automatically")
    print("\n💡 This is a fast, small model (1.3GB) perfect for analysis!\n")
    return False

def board_to_string(board):
    """Convert board state to readable format with enhanced visual clarity."""
    board_str = "OTHELLO BOARD (8x8 grid):\n"
    board_str += "    0   1   2   3   4   5   6   7  (COLUMNS)\n"
    board_str += "  +---+---+---+---+---+---+---+---+\n"

    for r in range(BOARD_SIZE):
        board_str += f"{r} |"  # Row number
        for c in range(BOARD_SIZE):
            if board[r, c] == 1:
                board_str += " B |"  # Black disc
            elif board[r, c] == -1:
                board_str += " W |"  # White disc
            else:
                board_str += " . |"  # Empty square

        # Add position annotations for key rows
        if r == 0:
            board_str += " <- Top edge"
        elif r == 7:
            board_str += " <- Bottom edge"
        board_str += "\n  +---+---+---+---+---+---+---+---+\n"

    board_str += "(ROWS)\n\n"

    # Add strategic annotations
    board_str += "LEGEND:\n"
    board_str += "  B = Black disc\n"
    board_str += "  W = White disc\n"
    board_str += "  . = Empty square\n"
    board_str += "  Corners (most valuable): (0,0), (0,7), (7,0), (7,7)\n"
    board_str += "  Edges: Row 0, Row 7, Column 0, Column 7\n\n"

    blacks, whites = count_discs(board)
    board_str += f"DISC COUNT: Black={blacks} discs, White={whites} discs\n"

    return board_str

def format_valid_moves_with_context(board, valid_moves, current_player):
    """Format valid moves with flip counts and strategic value indicators."""
    import numpy as np
    from logic import place_disc

    if not valid_moves:
        return "No valid moves available (must pass turn).\n"

    moves_str = "VALID MOVES (with analysis):\n"

    for i, (r, c) in enumerate(valid_moves, 1):
        # Simulate the move to count flips
        test_board = np.copy(board)
        place_disc(test_board, r, c, current_player)
        flips = np.sum(test_board != board) - 1  # -1 for the placed disc itself

        # Determine position type for strategic context
        is_corner = (r, c) in [(0, 0), (0, 7), (7, 0), (7, 7)]
        is_edge = (r == 0 or r == 7 or c == 0 or c == 7) and not is_corner

        if is_corner:
            position_type = "CORNER (best - permanent)"
        elif is_edge:
            position_type = "EDGE (good - stable)"
        else:
            position_type = "INTERIOR (neutral)"

        moves_str += f"  {i}. Row={r}, Col={c} -> Flips {flips} disc(s) [{position_type}]\n"

    moves_str += "\nCoordinate format: (Row, Column) where Row 0=top, Column 0=left\n"
    return moves_str

def get_board_analysis(board, current_player):
    """
    Uses local Ollama/Llama2 to analyze the board position.
    Free and runs on your computer!
    """
    try:
        print("📡 Calling local Ollama model...")

        player_name = "Black" if current_player == 1 else "White"

        valid_moves = get_valid_moves(board, current_player)

        board_str = board_to_string(board)
        moves_str = format_valid_moves_with_context(board, valid_moves, current_player)

        prompt = f"""You are analyzing an OTHELLO game. This is NOT chess.

{board_str}

CURRENT TURN: {player_name} to move

{moves_str}

TASK: First, verify you understand the board by stating how many Black and White discs you count. Then recommend the BEST move from the valid moves listed above.

Explain your choice in 2-3 sentences using Othello concepts:
- Corner control (corners are permanent and cannot be flipped)
- Edge stability (edges are harder to flip)
- Mobility (keeping move options open)
- Disc flipping count (immediate tactical gain)

Required format:
"I count [X] Black and [Y] White discs. Move Row=R, Col=C is best because [reason]."

Do NOT use chess terminology. Use only Othello/Reversi concepts."""

        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "temperature": 0.3,
            "options": {
                "num_predict": 400  # Slightly increased for verification step
            }
        }
        
        response = requests.post(OLLAMA_URL, json=payload, timeout=TIMEOUT)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Analysis received!")
            return result.get("response", "No response from model")
        else:
            print(f"❌ Error: Status code {response.status_code}")
            return f"Error: API returned status {response.status_code}"
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama. Is it running?")
        return "Error: Ollama not running. Start it with 'ollama serve'"
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        return f"Error: {str(e)}"

def get_game_summary(board, blacks, whites):
    """
    Analyzes the final game state using local Ollama.
    """
    try:
        print("📡 Calling local Ollama model for game summary...")

        if blacks > whites:
            winner = "Black"
            margin = blacks - whites
        elif whites > blacks:
            winner = "White"
            margin = whites - blacks
        else:
            winner = "Tie"
            margin = 0

        board_str = board_to_string(board)

        prompt = f"""You are analyzing the final state of an OTHELLO game. This is NOT chess.

{board_str}

GAME RESULT: {winner} wins by {margin} discs (Black={blacks}, White={whites})

TASK: Analyze this final board position and explain what determined the outcome.

In 3-4 sentences, discuss:
1. Which corners/edges were captured and their impact
2. One key strategic advantage the winner achieved
3. One Othello tip based on this game

Use only Othello concepts (corners, edges, mobility, stability, disc flipping).
NO chess terminology.

Keep your analysis focused on the visible board state above."""

        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "temperature": 0.3,
            "options": {
                "num_predict": 350
            }
        }
        
        response = requests.post(OLLAMA_URL, json=payload, timeout=TIMEOUT)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Game summary received!")
            return result.get("response", "No response from model")
        else:
            print(f"❌ Error: Status code {response.status_code}")
            return f"Error: API returned status {response.status_code}"
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama. Is it running?")
        return "Error: Ollama not running. Start it with 'ollama serve'"
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        return f"Error: {str(e)}"

def get_move_explanation(board, move_row, move_col, player):
    """
    Explains why a specific move was made using local Ollama.
    """
    try:
        print("📡 Calling local Ollama model...")

        player_name = "Black" if player == 1 else "White"

        board_str = board_to_string(board)

        # Determine position type for context
        is_corner = (move_row, move_col) in [(0, 0), (0, 7), (7, 0), (7, 7)]
        is_edge = (move_row == 0 or move_row == 7 or move_col == 0 or move_col == 7) and not is_corner

        if is_corner:
            position_hint = "This is a CORNER position (best strategic value)."
        elif is_edge:
            position_hint = "This is an EDGE position (good strategic value)."
        else:
            position_hint = "This is an INTERIOR position."

        prompt = f"""You are analyzing an OTHELLO game. This is NOT chess.

{board_str}

MOVE MADE: {player_name} placed a disc at Row={move_row}, Column={move_col}
{position_hint}

TASK: Evaluate this move's strength in 2-3 sentences.

Consider these Othello factors:
- Position value (corner > edge > interior)
- How many discs were flipped
- Whether it maintains mobility or opens dangerous moves for opponent
- Whether it secures stable discs

Format: "This move is [strong/weak/moderate] because [reason]."

Use only Othello terminology. NO chess terms."""

        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "temperature": 0.3,
            "options": {
                "num_predict": 250
            }
        }
        
        response = requests.post(OLLAMA_URL, json=payload, timeout=TIMEOUT)
        
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "No response from model")
        else:
            return f"Error: API returned status {response.status_code}"
            
    except requests.exceptions.ConnectionError:
        return "Error: Ollama not running"
    except Exception as e:
        return f"Error: {str(e)}"