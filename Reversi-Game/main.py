import pygame, sys, os, numpy as np
from constants import *
from logic import *
from ui import draw_board, end_screen, show_analysis
from ai import train_agent, load_model
from heatmap import generate_heatmap_surface
from undo import MoveHistory

# Try to import DSPy version, fallback to regular version
USE_DSPY = False
try:
    from explainability_dspy import get_board_analysis, get_game_summary, get_move_evaluation, check_dspy
    # Test if DSPy actually works
    if check_dspy():
        USE_DSPY = True
        print("🚀 Using DSPy-optimized explainability!")
    else:
        raise ImportError("DSPy check failed")
except (ImportError, Exception) as e:
    print(f"📝 Using standard explainability: {e}")
    from explainability_local import get_board_analysis, get_game_summary, check_ollama
    from undo import get_undo_analysis as get_move_evaluation_fallback
    
    def check_api_key():
        return check_ollama()

def board_to_obs(board):
    return board.astype(np.float32)

def check_api_key():
    """Check if Ollama/DSPy is running for AI analysis."""
    if USE_DSPY:
        return check_dspy()
    else:
        return check_ollama()

def main():
    print("Explainable RL Othello - options:")
    print("1) Human vs Human")
    print("2) Human vs Random AI")
    print("3) Human vs Trained AI")
    print("4) Train an AI now")
    choice = input("Choose option (1-4): ")

    has_api = check_api_key()
    
    model = None
    if choice == '1':
        print("Starting Human vs Human mode...")
        print("💡 Tips: Press 'H' for AI analysis | 'M' for move heatmap | 'U' to undo & analyze")
    elif choice == '2':
        print("Starting Human vs Random AI mode...")
        print("💡 Tips: Press 'H' for AI analysis | 'M' for move heatmap | 'U' to undo & analyze")
    elif choice == '3':
        print("Loading trained AI model...")
        model = load_model()
    elif choice == '4':
        steps = input("Training timesteps (default 20000): ")
        steps = int(steps) if steps.isdigit() else 20000
        model = train_agent(total_timesteps=steps)
    else:
        print("Invalid choice, defaulting to Human vs Human")
        choice = '1'
        has_api = check_api_key()

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Othello RL")
    clock = pygame.time.Clock()

    while True:
        board = init_board()
        current_player = 1
        running = True
        heatmap_surface = None  # Cached heatmap surface
        heatmap_board_hash = None  # Hash of board state when heatmap was generated
        move_history = MoveHistory()  # Track moves for undo
        analysis_text = None  # Store current analysis for sidebar display

        while running:
            valid_moves = get_valid_moves(board, current_player)

            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()

                # Clear analysis sidebar (press 'Q')
                if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                    if analysis_text is not None:
                        analysis_text = None
                        print("❌ Analysis cleared")

                # Handle help request (press 'H')
                if event.type == pygame.KEYDOWN and event.key == pygame.K_h:
                    if has_api and choice in ['1', '2']:
                        print("\n🤖 Analyzing board position...")
                        analysis_text = get_board_analysis(board, current_player)
                    else:
                        print("❌ AI analysis not available")
                
                # Undo move and get analysis (press 'U')
                if event.type == pygame.KEYDOWN and event.key == pygame.K_u:
                    if choice in ['1', '2']:
                        if move_history.can_undo():
                            print("\n⏮️  Undoing last move...")

                            # Get the move info before undoing
                            board_after = board.copy()
                            last_move = move_history.get_last_move()
                            board_before, move_player, move_row, move_col = last_move

                            # Undo the move
                            board = board_before.copy()
                            current_player = move_player  # Restore player turn
                            move_history.undo()  # Remove from history

                            # Clear heatmap
                            heatmap_surface = None
                            heatmap_board_hash = None

                            # Analyze the undone move
                            print("📊 Analyzing why this move was made...")
                            if USE_DSPY:
                                analysis_text = get_move_evaluation(board_before, board_after, move_player, move_row, move_col)
                            else:
                                from undo import get_undo_analysis
                                analysis_text = get_undo_analysis(board_before, board_after, move_player,
                                                            move_row, move_col, use_ai=has_api)

                            print(f"✅ Undone! Back to {('Black' if current_player == 1 else 'White')}'s turn")
                        else:
                            print("❌ No moves to undo!")
                    else:
                        print("❌ Undo only available in Human vs Human or Human vs Random AI modes")
                
                # Toggle heatmap (press 'M')
                if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                    if choice in ['1', '2']:
                        # Generate heatmap for current board state ONCE
                        current_hash = board.tobytes()
                        if heatmap_board_hash != current_hash:
                            print("🔥 Generating heatmap for current position...")
                            heatmap_surface = generate_heatmap_surface(screen, board, current_player)
                            heatmap_board_hash = current_hash
                            print("✅ Heatmap ready!")
                        else:
                            # Toggle off if pressing M again on same board
                            heatmap_surface = None
                            heatmap_board_hash = None
                            print("❌ Heatmap cleared")
                
                # Handle mouse clicks for human players
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Player 1 (Black) always plays by clicking
                    # Player 2 (White) only plays by clicking in Human vs Human mode
                    if current_player == 1 or (current_player == -1 and choice == '1'):
                        x, y = event.pos
                        BOARD_OFFSET = 40  # Account for row/column labels
                        # Check if click is within board area
                        if (BOARD_OFFSET <= x < BOARD_OFFSET + CELL_SIZE * BOARD_SIZE and
                            BOARD_OFFSET <= y < BOARD_OFFSET + CELL_SIZE * BOARD_SIZE):
                            r = (y - BOARD_OFFSET) // CELL_SIZE
                            c = (x - BOARD_OFFSET) // CELL_SIZE
                            if is_valid_move(board, r, c, current_player):
                                # Save move to history before making it
                                move_history.add_move(board, current_player, r, c)

                                place_disc(board, r, c, current_player)
                                current_player *= -1
                                # Clear heatmap after move is made
                                heatmap_surface = None
                                heatmap_board_hash = None
                                if not has_valid_moves(board, current_player):
                                    current_player *= -1

            # AI moves (only if not Human vs Human)
            if current_player == -1 and choice in ['2', '3', '4']:
                valid = get_valid_moves(board, current_player)
                if not valid:
                    current_player *= -1
                elif choice == '2':
                    # Random AI
                    r, c = valid[np.random.randint(len(valid))]
                    place_disc(board, r, c, current_player)
                    current_player *= -1
                    if not has_valid_moves(board, current_player):
                        current_player *= -1
                elif choice in ['3', '4'] and model:
                    # Trained AI
                    obs = board_to_obs(board)
                    action, _ = model.predict(obs, deterministic=True)
                    r, c = divmod(int(action), BOARD_SIZE)
                    if not is_valid_move(board, r, c, current_player):
                        if valid: r, c = valid[np.random.randint(len(valid))]
                    place_disc(board, r, c, current_player)
                    current_player *= -1
                    if not has_valid_moves(board, current_player):
                        current_player *= -1
                elif choice in ['3', '4'] and not model:
                    # Fallback to random if no model loaded
                    r, c = valid[np.random.randint(len(valid))]
                    place_disc(board, r, c, current_player)
                    current_player *= -1
                    if not has_valid_moves(board, current_player):
                        current_player *= -1

            if not has_valid_moves(board, 1) and not has_valid_moves(board, -1):
                b, w = count_discs(board)

                # Show game summary if API is available
                if has_api and choice in ['1', '2']:
                    print("\n🎮 Game Over! Generating analysis...")
                    analysis_text = get_game_summary(board, b, w)

                end_screen(screen, b, w)
                running = False

            draw_board(screen, board, valid_moves, analysis_text)
            
            # Draw cached heatmap surface if it exists
            if heatmap_surface is not None:
                screen.blit(heatmap_surface, (0, 0))
            
            pygame.display.flip()
            clock.tick(FPS)

if __name__ == "__main__":
    main()