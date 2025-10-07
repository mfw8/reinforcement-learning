import pygame, sys, os, numpy as np
from constants import *
from logic import *
from ui import draw_board, end_screen
from ai import train_agent, load_model

def board_to_obs(board):
    return board.astype(np.float32)

def main():
    print("Explainable RL Othello - options:")
    print("1) Human vs Human")
    print("2) Human vs Random AI")
    print("3) Human vs Trained AI")
    print("4) Train an AI now")
    choice = input("Choose option (1-4): ")

    model = None
    if choice == '4':
        steps = input("Training timesteps (default 20000): ")
        steps = int(steps) if steps.isdigit() else 20000
        model = train_agent(total_timesteps=steps)
    elif choice == '3':
        model = load_model()

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Othello RL")
    clock = pygame.time.Clock()

    while True:
        board = init_board()
        current_player = 1
        running = True
        while running:
            valid_moves = get_valid_moves(board, current_player)

            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if current_player == 1 or (current_player == -1 and choice == '1'):
                        x, y = event.pos
                        if y < HEIGHT-60:
                            r, c = y // CELL_SIZE, x // CELL_SIZE
                            if is_valid_move(board, r, c, current_player):
                                place_disc(board, r, c, current_player)
                                current_player *= -1
                                if not has_valid_moves(board, current_player):
                                    current_player *= -1

            if current_player == -1 and choice in ['2', '3', '4']:
                valid = get_valid_moves(board, current_player)
                if not valid:
                    current_player *= -1
                elif choice in ['2'] or model is None:
                    r, c = valid[np.random.randint(len(valid))]
                    place_disc(board, r, c, current_player)
                    current_player *= -1
                elif choice == '3' and model:
                    obs = board_to_obs(board)
                    action, _ = model.predict(obs, deterministic=True)
                    r, c = divmod(int(action), BOARD_SIZE)
                    if not is_valid_move(board, r, c, current_player):
                        if valid: r, c = valid[np.random.randint(len(valid))]
                    place_disc(board, r, c, current_player)
                    current_player *= -1

            if not has_valid_moves(board, 1) and not has_valid_moves(board, -1):
                b, w = count_discs(board)
                end_screen(screen, b, w)
                running = False

            draw_board(screen, board, valid_moves)
            pygame.display.flip()
            clock.tick(FPS)

if __name__ == "__main__":
    main()
