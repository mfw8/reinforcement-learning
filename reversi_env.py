import gymnasium as gym
from gymnasium import spaces
import numpy as np

class OthelloEnv(gym.Env):
    metadata = {"render_modes": ["human"], "render_fps": 4}

    def __init__(self, render_mode=None):
        super().__init__()
        self.size = 8  # standard Othello board size

        # Observation space: board state (8x8), values in {0: empty, 1: black, -1: white}
        self.observation_space = spaces.Box(low=-1, high=1, shape=(self.size, self.size), dtype=np.int8)

        # Action space: place a disc on an 8x8 grid (flat index from 0 to 63)
        self.action_space = spaces.Discrete(self.size * self.size)

        self.board = None
        self.current_player = 1  # 1 = black, -1 = white
        self.reset()

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)

        self.board = np.zeros((self.size, self.size), dtype=np.int8)
        mid = self.size // 2
        self.board[mid - 1, mid - 1] = -1
        self.board[mid, mid] = -1
        self.board[mid - 1, mid] = 1
        self.board[mid, mid - 1] = 1

        self.current_player = 1

        return self.board.copy(), {}

    def step(self, action):
        row, col = divmod(action, self.size)

        if not self.is_valid_move(row, col, self.current_player):
            # invalid move, penalize
            return self.board.copy(), -10, False, False, {"invalid": True}

        self.place_disc(row, col, self.current_player)

        # switch player
        self.current_player *= -1

        # check for end of game
        if not self.has_valid_moves(1) and not self.has_valid_moves(-1):
            done = True
            reward = self.get_winner_reward()
        else:
            done = False
            reward = 0

        return self.board.copy(), reward, done, False, {}

    def is_valid_move(self, row, col, player):
        if self.board[row, col] != 0:
            return False

        directions = [(-1, -1), (-1, 0), (-1, 1),
                      (0, -1),          (0, 1),
                      (1, -1),  (1, 0), (1, 1)]

        for dr, dc in directions:
            r, c = row + dr, col + dc
            found_opponent = False

            while 0 <= r < self.size and 0 <= c < self.size:
                if self.board[r, c] == -player:
                    found_opponent = True
                elif self.board[r, c] == player and found_opponent:
                    return True
                else:
                    break
                r += dr
                c += dc

        return False

    def place_disc(self, row, col, player):
        self.board[row, col] = player

        directions = [(-1, -1), (-1, 0), (-1, 1),
                      (0, -1),          (0, 1),
                      (1, -1),  (1, 0), (1, 1)]

        for dr, dc in directions:
            r, c = row + dr, col + dc
            to_flip = []

            while 0 <= r < self.size and 0 <= c < self.size:
                if self.board[r, c] == -player:
                    to_flip.append((r, c))
                elif self.board[r, c] == player and to_flip:
                    for rr, cc in to_flip:
                        self.board[rr, cc] = player
                    break
                else:
                    break
                r += dr
                c += dc

    def has_valid_moves(self, player):
        for r in range(self.size):
            for c in range(self.size):
                if self.is_valid_move(r, c, player):
                    return True
        return False

    def get_winner_reward(self):
        black_count = np.sum(self.board == 1)
        white_count = np.sum(self.board == -1)

        if black_count > white_count:
            return 1 if self.current_player == -1 else -1
        elif white_count > black_count:
            return 1 if self.current_player == 1 else -1
        else:
            return 0

    def render(self):
        print("Current player:", "Black" if self.current_player == 1 else "White")
        for row in self.board:
            print(" ".join(["." if x == 0 else ("B" if x == 1 else "W") for x in row]))
        print()


if __name__ == "__main__":
    env = OthelloEnv()
    obs, _ = env.reset()
    env.render()

    for _ in range(10):
        action = env.action_space.sample()
        obs, reward, done, _, info = env.step(action)
        env.render()
        if done:
            print("Game Over, reward:", reward)
            break
