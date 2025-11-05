import numpy as np
import requests
import json
from logic import count_discs, get_valid_moves
from constants import BOARD_SIZE

class MoveHistory:
    """Tracks move history for undo functionality."""
    
    def __init__(self):
        self.history = []  # List of (board_state, player, move_row, move_col)
    
    def add_move(self, board, player, row, col):
        """Add a move to history."""
        self.history.append((board.copy(), player, row, col))
    
    def can_undo(self):
        """Check if there are moves to undo."""
        return len(self.history) > 0
    
    def undo(self):
        """Remove and return the last move."""
        if self.can_undo():
            return self.history.pop()
        return None
    
    def get_last_move(self):
        """Get the last move without removing it."""
        if self.can_undo():
            return self.history[-1]
        return None
    
    def clear(self):
        """Clear all history."""
        self.history = []

def analyze_move_quality(board_before, board_after, player, row, col):
    """
    Analyze why a move was good or bad using heuristics.
    Returns a detailed explanation string.
    """
    explanation = []
    player_name = "Black" if player == 1 else "White"
    
    explanation.append(f"Analysis of {player_name}'s move at ({row}, {col}):\n")
    
    # 1. Position type analysis
    corners = [(0,0), (0,7), (7,0), (7,7)]
    edges = [(r,c) for r in range(8) for c in range(8) 
             if (r == 0 or r == 7 or c == 0 or c == 7) and (r,c) not in corners]
    x_squares = [(1,1), (1,6), (6,1), (6,6)]  # Dangerous squares next to corners
    c_squares = [(0,1), (1,0), (0,6), (1,7), (6,0), (7,1), (6,7), (7,6)]  # Edge of corner
    
    if (row, col) in corners:
        explanation.append("✅ EXCELLENT! You captured a CORNER - the most valuable position!")
        explanation.append("   Corners can never be flipped. This is almost always good.")
    elif (row, col) in x_squares:
        explanation.append("⚠️ WARNING! You played an X-square (next to corner).")
        explanation.append("   This often gives your opponent the corner. Usually a BAD move.")
    elif (row, col) in c_squares:
        explanation.append("⚠️ RISKY! You played a C-square (edge of corner).")
        explanation.append("   This can give your opponent access to the corner.")
    elif (row, col) in edges:
        explanation.append("✓ Good! Edge positions are generally stable.")
    else:
        explanation.append("• Interior move - stability depends on surrounding pieces.")
    
    # 2. Disc count analysis
    before_blacks, before_whites = count_discs(board_before)
    after_blacks, after_whites = count_discs(board_after)
    
    if player == 1:
        discs_gained = after_blacks - before_blacks
        explanation.append(f"\n• You flipped {discs_gained - 1} opponent disc(s).")
    else:
        discs_gained = after_whites - before_whites
        explanation.append(f"\n• You flipped {discs_gained - 1} opponent disc(s).")
    
    if discs_gained > 5:
        explanation.append("  ⚠️ Flipping many discs in the early/mid game can be BAD!")
        explanation.append("  It often gives your opponent more moves (mobility).")
    
    # 3. Mobility analysis
    opponent = -player
    moves_before = len(get_valid_moves(board_before, opponent))
    moves_after = len(get_valid_moves(board_after, opponent))
    
    explanation.append(f"\n• Opponent mobility: {moves_before} → {moves_after} moves")
    if moves_after > moves_before:
        explanation.append("  ⚠️ BAD! You gave opponent MORE moves.")
    elif moves_after < moves_before:
        explanation.append("  ✓ Good! You reduced opponent's options.")
    
    # 4. Corner access analysis
    gave_corner = False
    for corner in corners:
        cr, cc = corner
        if board_before[cr, cc] == 0 and board_after[cr, cc] == opponent:
            gave_corner = True
            explanation.append(f"\n❌ CRITICAL ERROR! Opponent captured corner ({cr},{cc})!")
    
    if not gave_corner:
        # Check if opponent now has access to corners
        opponent_moves_after = get_valid_moves(board_after, opponent)
        corner_access = [move for move in opponent_moves_after if move in corners]
        if corner_access:
            explanation.append(f"\n⚠️ WARNING! Opponent can now take corner: {corner_access}")
    
    # 5. Strategic advice
    explanation.append("\n📚 Key Strategy Tips:")
    explanation.append("  1. Corners are GOLD - always take them if possible")
    explanation.append("  2. Avoid X-squares unless you have a very good reason")
    explanation.append("  3. In early/mid game, FEWER discs is often better")
    explanation.append("  4. Limit opponent's mobility (# of moves)")
    explanation.append("  5. Edges are generally good, stable positions")
    
    return "\n".join(explanation)

def analyze_move_with_ai(board_before, board_after, player, row, col):
    """
    Use local Ollama to analyze why a move was good or bad.
    """
    try:
        from explainability_local import board_to_string, OLLAMA_URL, MODEL_NAME, TIMEOUT
        
        player_name = "Black" if player == 1 else "White"
        
        before_str = board_to_string(board_before)
        after_str = board_to_string(board_after)
        
        before_blacks, before_whites = count_discs(board_before)
        after_blacks, after_whites = count_discs(board_after)
        
        prompt = f"""You are an Othello expert. Analyze this move that was just undone.

BEFORE the move:
{before_str}

AFTER {player_name} played at ({row}, {col}):
{after_str}

Score change: Black {before_blacks}→{after_blacks}, White {before_whites}→{after_whites}

Explain:
1. Was this a good or bad move? Why?
2. What strategic mistakes were made (if any)?
3. What would have been a better alternative?
4. Key lesson to learn from this move

Be honest and educational. Use Othello terminology (corners, edges, mobility, discs)."""

        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "temperature": 0.7,
            "options": {
                "num_predict": 400
            }
        }
        
        print("📡 Analyzing your move with AI...")
        response = requests.post(OLLAMA_URL, json=payload, timeout=TIMEOUT)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Analysis complete!")
            return result.get("response", "No response from model")
        else:
            print(f"❌ AI request failed, using heuristic analysis")
            return analyze_move_quality(board_before, board_after, player, row, col)
            
    except Exception as e:
        print(f"❌ AI analysis failed: {e}")
        print("Using heuristic analysis instead...")
        return analyze_move_quality(board_before, board_after, player, row, col)

def get_undo_analysis(board_before, board_after, player, row, col, use_ai=True):
    """
    Get analysis of an undone move.
    Returns explanation string.
    """
    if use_ai:
        return analyze_move_with_ai(board_before, board_after, player, row, col)
    else:
        return analyze_move_quality(board_before, board_after, player, row, col)