import numpy as np
from constants import BOARD_SIZE

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

def get_valid_moves(board, player):
    """Returns a list of (row, col) tuples for all valid moves."""
    valid = []
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if is_valid_move(board, r, c, player):
                valid.append((r, c))
    return valid

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