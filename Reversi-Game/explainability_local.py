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
    """Convert board state to readable format for the model."""
    board_str = "Othello Board State:\n"
    board_str += "  0 1 2 3 4 5 6 7\n"
    for r in range(BOARD_SIZE):
        board_str += f"{r} "
        for c in range(BOARD_SIZE):
            if board[r, c] == 1:
                board_str += "B "  # Black
            elif board[r, c] == -1:
                board_str += "W "  # White
            else:
                board_str += ". "
        board_str += "\n"
    
    blacks, whites = count_discs(board)
    board_str += f"\nScore: Black {blacks} - White {whites}\n"
    return board_str

def get_board_analysis(board, current_player):
    """
    Uses local Ollama/Llama2 to analyze the board position.
    Free and runs on your computer!
    """
    try:
        print("📡 Calling local Ollama model...")
        
        player_name = "Black" if current_player == 1 else "White"
        
        valid_moves = get_valid_moves(board, current_player)
        valid_moves_str = ", ".join([f"({r},{c})" for r, c in valid_moves])
        
        board_str = board_to_string(board)
        
        prompt = f"""You are analyzing an OTHELLO (Reversi) game, NOT chess. In Othello, there are only BLACK discs (B) and WHITE discs (W) on an 8x8 board. Players flip opponent discs by sandwiching them.

{board_str}

Current Player: {player_name}
Valid Moves (row,col): {valid_moves_str}

Analyze:
1. Who is winning? Count the B and W discs.
2. Best move for {player_name} and why?
3. One strategic tip for Othello

Use ONLY Othello terminology (discs, flip, corners, edges). NO chess terms."""

        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "temperature": 0.7,
            "options": {
                "num_predict": 300  # Limit response length for speed
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
        
        prompt = f"""You are analyzing an OTHELLO (Reversi) game, NOT chess. Othello uses BLACK discs (B) and WHITE discs (W). Players flip opponent discs by sandwiching them between their own discs.

{board_str}

Final Result: {winner} wins by {margin} discs (Black {blacks}, White {whites})

Analyze:
1. What did the winner do well? (Consider corners, edges, mobility)
2. What could the loser improve?
3. Two Othello strategy tips (corners, edges, mobility control)

Use ONLY Othello terminology. NO chess terms like king, queen, checkmate."""

        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "temperature": 0.7,
            "options": {
                "num_predict": 300
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
        
        prompt = f"""You are analyzing an OTHELLO (Reversi) game, NOT chess. Othello uses BLACK discs (B) and WHITE discs (W).

{board_str}

Move: {player_name} placed a disc at row {move_row}, column {move_col}

Is this a strong Othello move? Explain briefly using Othello concepts (corners, edges, mobility, disc flipping).

NO chess terminology."""

        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "temperature": 0.7,
            "options": {
                "num_predict": 200
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