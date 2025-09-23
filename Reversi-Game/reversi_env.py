import pygame
import sys
import numpy as np
import gymnasium as gym
from gymnasium import spaces
import os

# Stable-Baselines3
try:
    from stable_baselines3 import PPO
    from stable_baselines3.common.vec_env import DummyVecEnv
    SB3_AVAILABLE = True
except Exception:
    SB3_AVAILABLE = False

# --- Settings ---
BOARD_SIZE = 8
CELL_SIZE = 80
WIDTH, HEIGHT = CELL_SIZE * BOARD_SIZE, CELL_SIZE * BOARD_SIZE + 60
FPS = 30
MODEL_PATH = "othello_ppo.zip"

# Colors
GREEN = (0, 128, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)

# Score tracker
total_scores = {"Black": 0, "White": 0}

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
    directions = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
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

# --- Gym Environment for Training ---
class OthelloGymEnv(gym.Env):
    """Gym environment wrapper for Othello game using the same logic.
    Observation: 8x8 board with values {-1,0,1}
    Action: Discrete 64 (place at index 0..63)
    Reward: 0 for non-terminal moves; at terminal +1/-1/tie for black win/lose/tie (from black's perspective)
    """
    metadata = {"render.modes": ["human"]}

    def __init__(self):
        super().__init__()
        self.size = BOARD_SIZE
        self.observation_space = spaces.Box(low=-1, high=1, shape=(self.size, self.size), dtype=np.int8)
        self.action_space = spaces.Discrete(self.size * self.size)
        self.reset()

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)  # ensure seeding works properly
        self.board = init_board()
        self.current_player = 1  # black starts
        return self.board.copy(), {}


    def step(self, action):
        row, col = divmod(int(action), self.size)
        info = {}

        if not is_valid_move(self.board, row, col, self.current_player):
            # Invalid move = small penalty
            return self.board.copy(), -0.1, False, False, info

        place_disc(self.board, row, col, self.current_player)
        self.current_player *= -1

        # Check for end of game
        done = not has_valid_moves(self.board, 1) and not has_valid_moves(self.board, -1)
        if done:
            blacks, whites = count_discs(self.board)
            if blacks > whites:
                reward = 1.0
            elif whites > blacks:
                reward = -1.0
            else:
                reward = 0.0
            return self.board.copy(), reward, True, False, info
        else:
            return self.board.copy(), 0.0, False, False, info


    def render(self, mode='human'):
        # simple text render
        for r in range(self.size):
            print(' '.join(['.' if x==0 else ('B' if x==1 else 'W') for x in self.board[r]]))
        print()

def train_agent(total_timesteps=20000):
    if not SB3_AVAILABLE:
        raise RuntimeError("Stable-Baselines3 not available. Install with: pip install stable-baselines3[extra]")

    def make_env():
        return OthelloGymEnv()

    env = DummyVecEnv([make_env])
    model = PPO('MlpPolicy', env, verbose=1)
    model.learn(total_timesteps=total_timesteps)
    model.save(MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")
    return model

# --- Pygame Rendering ---
def draw_board(screen, board):
    screen.fill(GREEN)

    # Grid lines
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(screen, BLACK, (x, 0), (x, HEIGHT-60))
    for y in range(0, HEIGHT-60, CELL_SIZE):
        pygame.draw.line(screen, BLACK, (0, y), (WIDTH, y))

    # Discs
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r, c] == 1:  # Black
                pygame.draw.circle(screen, BLACK, (c*CELL_SIZE+CELL_SIZE//2, r*CELL_SIZE+CELL_SIZE//2), CELL_SIZE//2 - 5)
            elif board[r, c] == -1:  # White
                pygame.draw.circle(screen, WHITE, (c*CELL_SIZE+CELL_SIZE//2, r*CELL_SIZE+CELL_SIZE//2), CELL_SIZE//2 - 5)

    # Score tracker
    font = pygame.font.SysFont(None, 30)
    blacks, whites = count_discs(board)
    score_text = font.render(f"Black: {blacks}  White: {whites}", True, BLACK)
    total_text = font.render(f"Wins → Black: {total_scores['Black']} | White: {total_scores['White']}", True, BLACK)
    screen.blit(score_text, (10, HEIGHT-55))
    screen.blit(total_text, (10, HEIGHT-30))

# --- End screen UI ---

def end_screen(screen, blacks, whites):
    font = pygame.font.SysFont(None, 40)
    if blacks > whites:
        winner = "Black wins!"
        total_scores["Black"] += 1
    elif whites > blacks:
        winner = "White wins!"
        total_scores["White"] += 1
    else:
        winner = "It's a tie!"

    screen.fill(GREEN)
    text = font.render(winner, True, BLACK)
    score_text = font.render(f"Black: {blacks}  White: {whites}", True, BLACK)
    total_text = font.render(f"Wins → Black: {total_scores['Black']} | White: {total_scores['White']}", True, BLACK)
    cont_text = font.render("Press C to continue or Q to quit", True, BLACK)

    screen.blit(text, (50, 100))
    screen.blit(score_text, (50, 160))
    screen.blit(total_text, (50, 220))
    screen.blit(cont_text, (50, 280))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    waiting = False
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

# converts board to observation for SB3

def board_to_obs(board):
    # keep (8,8) shape for consistency with training
    return board.astype(np.float32)


# --- Main game with opponent selection ---

def main():
    # Check SB3 availability and inform user
    print("Explainable RL Othello - options:")
    print("1) Human vs Human")
    print("2) Human vs Random AI")
    print("3) Human vs Trained AI")
    print("4) Train an AI now (requires Stable-Baselines3)")
    choice = input("Choose option (1-4): ")

    model = None
    if choice == '4':
        if not SB3_AVAILABLE:
            print("Stable-Baselines3 is not installed. Install via: pip install stable-baselines3[extra]")
            return
        steps = input("Enter training timesteps (e.g. 20000): ")
        try:
            steps = int(steps)
        except Exception:
            steps = 20000
        model = train_agent(total_timesteps=steps)
    elif choice == '3':
        if not SB3_AVAILABLE:
            print("Stable-Baselines3 not available; falling back to Random AI.")
            choice = '2'
        else:
            if os.path.exists(MODEL_PATH):
                model = PPO.load(MODEL_PATH)
                print(f"Loaded model from {MODEL_PATH}")
            else:
                print(f"No model found at {MODEL_PATH}. Please train one first (option 4) or choose 2 for Random AI.")
                return

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Othello - Click to Play")
    clock = pygame.time.Clock()

    while True:  # allow multiple games (continue/quit handled after each game)
        board = init_board()
        current_player = 1  # 1 = Black (human), -1 = White (human or AI)
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # Handle human click if it's a human player's turn
                if event.type == pygame.MOUSEBUTTONDOWN and current_player == 1:
                    x, y = event.pos
                    if y < HEIGHT-60:
                        row, col = y // CELL_SIZE, x // CELL_SIZE
                        if is_valid_move(board, row, col, current_player):
                            place_disc(board, row, col, current_player)
                            current_player *= -1
                            # skip turn logic
                            if not has_valid_moves(board, current_player):
                                current_player *= -1

                # Keyboard shortcut to quit mid-game
                if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

            # If it's AI's turn, decide move
            if current_player == -1:
                if choice == '2' or (choice == '3' and model is None):
                    # Random AI
                    valid = [(r,c) for r in range(BOARD_SIZE) for c in range(BOARD_SIZE) if is_valid_move(board, r, c, current_player)]
                    if valid:
                        r,c = valid[np.random.randint(len(valid))]
                        place_disc(board, r, c, current_player)
                        current_player *= -1
                        if not has_valid_moves(board, current_player):
                            current_player *= -1
                elif choice == '3' and model is not None:
                    obs = board_to_obs(board)
                    action, _ = model.predict(obs, deterministic=True)
                    # action may be invalid; if so, pick nearest valid or random valid
                    row, col = divmod(int(action), BOARD_SIZE)
                    if not is_valid_move(board, row, col, current_player):
                        valid = [(r,c) for r in range(BOARD_SIZE) for c in range(BOARD_SIZE) if is_valid_move(board, r, c, current_player)]
                        if valid:
                            r,c = valid[np.random.randint(len(valid))]
                            place_disc(board, r, c, current_player)
                        # else no valid moves
                    else:
                        place_disc(board, row, col, current_player)
                    current_player *= -1
                    if not has_valid_moves(board, current_player):
                        current_player *= -1

            # Check end condition
            if not has_valid_moves(board, 1) and not has_valid_moves(board, -1):
                blacks, whites = count_discs(board)
                end_screen(screen, blacks, whites)
                running = False

            draw_board(screen, board)
            pygame.display.flip()
            clock.tick(FPS)


if __name__ == "__main__":
    print("Dependencies: pygame, numpy, gym, stable-baselines3 (optional)")
    print("Install with: pip install pygame numpy gym stable-baselines3[extra]")
    main()
