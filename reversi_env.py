import pygame
import numpy as np

# --- Settings ---
BOARD_SIZE = 8
CELL_SIZE = 80
WIDTH, HEIGHT = CELL_SIZE * BOARD_SIZE, CELL_SIZE * BOARD_SIZE
FPS = 30

# Colors
GREEN = (0, 128, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)

# --- Game Logic ---
def init_board():
    board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=np.int8)
    mid = BOARD_SIZE // 2
    board[mid-1, mid-1] = -1
    board[mid, mid] = -1
    board[mid-1, mid] = 1
    board[mid, mid-1] = 1
    return board

def is_valid_move(board, row, col, player):
    if board[row, col] != 0:
        return False

    directions = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
    for dr, dc in directions:
        r, c = row+dr, col+dc
        found_opponent = False
        while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
            if board[r, c] == -player:
                found_opponent = True
            elif board[r, c] == player and found_opponent:
                return True
            else:
                break
            r += dr
            c += dc
    return False

def place_disc(board, row, col, player):
    board[row, col] = player
    directions = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
    for dr, dc in directions:
        r, c = row+dr, col+dc
        to_flip = []
        while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
            if board[r, c] == -player:
                to_flip.append((r, c))
            elif board[r, c] == player and to_flip:
                for rr, cc in to_flip:
                    board[rr, cc] = player
                break
            else:
                break
            r += dr
            c += dc

def has_valid_moves(board, player):
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if is_valid_move(board, r, c, player):
                return True
    return False

def count_discs(board):
    blacks = np.sum(board == 1)
    whites = np.sum(board == -1)
    return blacks, whites

# --- Pygame Rendering ---
def draw_board(screen, board):
    screen.fill(GREEN)

    # Grid lines
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(screen, BLACK, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, BLACK, (0, y), (WIDTH, y))

    # Discs
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r, c] == 1:  # Black
                pygame.draw.circle(screen, BLACK, (c*CELL_SIZE+CELL_SIZE//2, r*CELL_SIZE+CELL_SIZE//2), CELL_SIZE//2 - 5)
            elif board[r, c] == -1:  # White
                pygame.draw.circle(screen, WHITE, (c*CELL_SIZE+CELL_SIZE//2, r*CELL_SIZE+CELL_SIZE//2), CELL_SIZE//2 - 5)

# --- Main Game Loop ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Othello - Click to Play")
    clock = pygame.time.Clock()

    board = init_board()
    current_player = 1  # Black starts
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                row, col = y // CELL_SIZE, x // CELL_SIZE
                if is_valid_move(board, row, col, current_player):
                    place_disc(board, row, col, current_player)
                    current_player *= -1

                    # Skip turn if opponent has no moves
                    if not has_valid_moves(board, current_player):
                        current_player *= -1

                    # End game if no moves for both
                    if not has_valid_moves(board, 1) and not has_valid_moves(board, -1):
                        blacks, whites = count_discs(board)
                        print("Game Over! Black:", blacks, "White:", whites)
                        running = False

        draw_board(screen, board)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
