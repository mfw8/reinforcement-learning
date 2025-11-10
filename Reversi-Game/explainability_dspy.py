"""
DSPy-optimized explainability for Othello game.
Uses structured prompting and optimization for better AI responses.
"""

import dspy
from logic import count_discs, get_valid_moves
from constants import BOARD_SIZE

# Configure DSPy to use local Ollama
ollama_lm = dspy.OllamaLocal(
    model="llama3.2:1b",
    base_url="http://localhost:11434",
    max_tokens=500
)
dspy.settings.configure(lm=ollama_lm)

def board_to_string(board):
    """Convert board state to readable format."""
    board_str = "Othello Board (B=Black, W=White, .=Empty):\n"
    board_str += "  0 1 2 3 4 5 6 7\n"
    for r in range(BOARD_SIZE):
        board_str += f"{r} "
        for c in range(BOARD_SIZE):
            if board[r, c] == 1:
                board_str += "B "
            elif board[r, c] == -1:
                board_str += "W "
            else:
                board_str += ". "
        board_str += "\n"
    
    blacks, whites = count_discs(board)
    board_str += f"\nCurrent Score: Black={blacks}, White={whites}"
    return board_str

# DSPy Signature for board analysis
class AnalyzeOthelloPosition(dspy.Signature):
    """Analyze an Othello board position and suggest the best move."""
    
    board_state = dspy.InputField(desc="Current Othello board state with piece positions")
    current_player = dspy.InputField(desc="Current player name (Black or White)")
    valid_moves = dspy.InputField(desc="List of valid moves in (row,col) format")
    
    board_analysis = dspy.OutputField(desc="Brief analysis of who is winning and why (2-3 sentences)")
    best_move = dspy.OutputField(desc="The best move to play as (row,col) with reasoning (2-3 sentences)")
    strategy_tip = dspy.OutputField(desc="One key strategic tip for improving (1-2 sentences)")

# DSPy Signature for game summary
class AnalyzeOthelloGame(dspy.Signature):
    """Analyze a completed Othello game and provide learning insights."""
    
    final_board = dspy.InputField(desc="Final Othello board state")
    winner = dspy.InputField(desc="Game winner (Black/White/Tie)")
    final_score = dspy.InputField(desc="Final score as 'Black X, White Y'")
    
    winner_strengths = dspy.OutputField(desc="What the winner did well (2-3 sentences)")
    loser_mistakes = dspy.OutputField(desc="What the loser could improve (2-3 sentences)")
    key_strategies = dspy.OutputField(desc="Two specific Othello strategy tips (corners, edges, mobility)")

# DSPy Signature for move evaluation
class EvaluateOthelloMove(dspy.Signature):
    """Evaluate whether an Othello move was good or bad."""
    
    board_before = dspy.InputField(desc="Board state before the move")
    board_after = dspy.InputField(desc="Board state after the move")
    player = dspy.InputField(desc="Player who made the move (Black or White)")
    move_position = dspy.InputField(desc="Move position as (row,col)")
    
    move_quality = dspy.OutputField(desc="Is this move good or bad? Rate 1-10 with explanation (2-3 sentences)")
    strategic_impact = dspy.OutputField(desc="Strategic implications of this move (2-3 sentences)")
    better_alternative = dspy.OutputField(desc="What would have been better? (1-2 sentences)")

# Module classes using Chain of Thought
class BoardAnalyzer(dspy.Module):
    def __init__(self):
        super().__init__()
        self.analyze = dspy.ChainOfThought(AnalyzeOthelloPosition)
    
    def forward(self, board_state, current_player, valid_moves):
        result = self.analyze(
            board_state=board_state,
            current_player=current_player,
            valid_moves=valid_moves
        )
        return result

class GameAnalyzer(dspy.Module):
    def __init__(self):
        super().__init__()
        self.analyze = dspy.ChainOfThought(AnalyzeOthelloGame)
    
    def forward(self, final_board, winner, final_score):
        result = self.analyze(
            final_board=final_board,
            winner=winner,
            final_score=final_score
        )
        return result

class MoveEvaluator(dspy.Module):
    def __init__(self):
        super().__init__()
        self.evaluate = dspy.ChainOfThought(EvaluateOthelloMove)
    
    def forward(self, board_before, board_after, player, move_position):
        result = self.evaluate(
            board_before=board_before,
            board_after=board_after,
            player=player,
            move_position=move_position
        )
        return result

# Initialize modules
board_analyzer = BoardAnalyzer()
game_analyzer = GameAnalyzer()
move_evaluator = MoveEvaluator()

def check_dspy():
    """Check if DSPy and Ollama are available."""
    try:
        import dspy
        # Try a simple test
        test_result = ollama_lm("Test", max_tokens=5)
        print("✅ DSPy with Ollama is ready!")
        return True
    except ImportError:
        print("❌ DSPy not installed. Install with: pip install dspy-ai")
        return False
    except Exception as e:
        print(f"❌ DSPy/Ollama error: {e}")
        print("Make sure Ollama is running with: ollama serve")
        return False

def get_board_analysis(board, current_player):
    """
    Analyze the current board position using DSPy-optimized prompts.
    """
    try:
        print("🤖 Analyzing with DSPy...")
        
        player_name = "Black" if current_player == 1 else "White"
        board_state = board_to_string(board)
        valid_moves = get_valid_moves(board, current_player)
        moves_str = ", ".join([f"({r},{c})" for r, c in valid_moves])
        
        # Use DSPy module
        result = board_analyzer(
            board_state=board_state,
            current_player=player_name,
            valid_moves=moves_str
        )
        
        # Format the response
        analysis = f"""🎯 BOARD ANALYSIS for {player_name}

📊 Position Assessment:
{result.board_analysis}

🎲 Best Move Recommendation:
{result.best_move}

💡 Strategy Tip:
{result.strategy_tip}
"""
        
        print("✅ DSPy analysis complete!")
        return analysis
        
    except Exception as e:
        print(f"❌ DSPy analysis failed: {e}")
        # Fallback to simple analysis
        return f"Error: Could not analyze position. {str(e)}"

def get_game_summary(board, blacks, whites):
    """
    Analyze the completed game using DSPy.
    """
    try:
        print("🤖 Generating game summary with DSPy...")
        
        if blacks > whites:
            winner = "Black"
        elif whites > blacks:
            winner = "White"
        else:
            winner = "Tie"
        
        final_board = board_to_string(board)
        final_score = f"Black {blacks}, White {whites}"
        
        # Use DSPy module
        result = game_analyzer(
            final_board=final_board,
            winner=winner,
            final_score=final_score
        )
        
        # Format the response
        summary = f"""🎮 GAME SUMMARY

🏆 Result: {winner} wins! ({final_score})

✨ What the Winner Did Well:
{result.winner_strengths}

📚 Areas for Improvement:
{result.loser_mistakes}

🎯 Key Strategies to Remember:
{result.key_strategies}
"""
        
        print("✅ Game summary complete!")
        return summary
        
    except Exception as e:
        print(f"❌ DSPy game summary failed: {e}")
        return f"Error: Could not generate summary. {str(e)}"

def get_move_evaluation(board_before, board_after, player, row, col):
    """
    Evaluate a move using DSPy.
    """
    try:
        print("🤖 Evaluating move with DSPy...")
        
        player_name = "Black" if player == 1 else "White"
        before_str = board_to_string(board_before)
        after_str = board_to_string(board_after)
        move_pos = f"({row},{col})"
        
        # Use DSPy module
        result = move_evaluator(
            board_before=before_str,
            board_after=after_str,
            player=player_name,
            move_position=move_pos
        )
        
        # Format the response
        evaluation = f"""🔍 MOVE EVALUATION

Move: {player_name} played at {move_pos}

⭐ Move Quality:
{result.move_quality}

🎯 Strategic Impact:
{result.strategic_impact}

💭 Better Alternative:
{result.better_alternative}
"""
        
        print("✅ Move evaluation complete!")
        return evaluation
        
    except Exception as e:
        print(f"❌ DSPy evaluation failed: {e}")
        return f"Error: Could not evaluate move. {str(e)}"