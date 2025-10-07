import gymnasium as gym
from gymnasium import spaces
from logic import *
import numpy as np

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
                reward = 1.04
                
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