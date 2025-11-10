import pygame, sys, os, numpy as np
from constants import *
from logic import *
from ui import draw_board, end_screen, show_analysis
from ai import train_agent, load_model
from heatmap import generate_heatmap_surface
from undo import MoveHistory

# Try to import DSPy version, fallback to regular version
try:
    from explainability_dspy import get_board_analysis, get_game_summary, get_move_evaluation, check_dspy
    USE_DSPY = True
    print("🚀 Using DSPy-optimized explainability!")
except ImportError:
    from explainability_local import get_board_analysis, get_game_summary, check_ollama
    from undo import get_undo_analysis as get_move_evaluation
    USE_DSPY = False
    print("📝 Using standard explainability (install dspy-ai for optimization)")

def board_to_obs(board):
    return board.astype(np.float32)

def check_api_key():
    """Check if Ollama is running for free local AI analysis."""
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
        
        while running:
            valid_moves = get_valid_moves(board, current_player)

            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                
                # Handle help request (press 'H')
                if event.type == pygame.KEYDOWN and event.key == pygame.K_h:
                    if has_api and choice in ['1', '2']:
                        print("\n🤖 Analyzing board position...")
                        analysis = get_board_analysis(board, current_player)
                        show_analysis(screen, analysis)
                
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
                            analysis = get_undo_analysis(board_before, board_after, move_player, 
                                                        move_row, move_col, use_ai=has_api)
                            show_analysis(screen, analysis)
                            
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
                        if y < HEIGHT-60:
                            r, c = y // CELL_SIZE, x // CELL_SIZE
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
                    summary = get_game_summary(board, b, w)
                    show_analysis(screen, summary)
                
                end_screen(screen, b, w)
                running = False

            draw_board(screen, board, valid_moves)
            
            # Draw cached heatmap surface if it exists
            if heatmap_surface is not None:
                screen.blit(heatmap_surface, (0, 0))
            
            pygame.display.flip()
            clock.tick(FPS)

if __name__ == "__main__":
    main()