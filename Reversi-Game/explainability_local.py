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
    print("  1. Download Ollama from: https://ollama.ai")
    print("  2. Install and run it")
    print("  3. In a terminal, run: ollama pull llama2")
    print("  4. Ollama will start automatically on localhost:11434")
    print("\n💡 Llama2 is free and runs on your computer!\n")
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
        
        prompt = f"""You are an expert Othello/Reversi strategist. Analyze this board position and provide advice.

{board_str}

Current Player: {player_name}
Valid Moves: {valid_moves_str}

Please provide:
1. Brief analysis of the current board state (who is winning and why)
2. The BEST move to play and why
3. Specific tips to improve {player_name}'s strategy

Keep it concise and practical. Do not use chess terminology."""

        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "temperature": 0.7,
        }
        
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        
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
        
        prompt = f"""You are an expert Othello/Reversi strategist. Analyze this completed game.

{board_str}

Final Result: {winner} wins by {margin} points (Black {blacks}, White {whites})

Please provide:
1. What the winner did well
2. What the loser could have done better
3. Three specific strategy tips for improving at Othello
4. Common beginner mistakes to avoid

Keep it constructive and educational."""

        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "temperature": 0.7,
        }
        
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        
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
        
        prompt = f"""You are an expert Othello/Reversi strategist. Evaluate this move.

{board_str}

Move: {player_name} places a disc at position ({move_row}, {move_col})

Please analyze:
1. Is this a strong move? Why or why not?
2. What are the strategic implications?
3. How does this compare to alternatives?

Be honest about whether this is a good or bad move. Keep it brief."""

        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "temperature": 0.7,
        }
        
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "No response from model")
        else:
            return f"Error: API returned status {response.status_code}"
            
    except requests.exceptions.ConnectionError:
        return "Error: Ollama not running"
    except Exception as e:
        return f"Error: {str(e)}"