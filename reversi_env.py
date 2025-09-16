import gymnasium as gym
from gymnasium import spaces
import numpy as np

class OthelloEnv(gym.Env):
    """
    A custom Gymnasium environment for the game Othello (Reversi).
    Board is 8x8, with values:
      - 0 = empty cell
      - 1 = black disc
      - -1 = white disc

    Current player alternates between 1 (black) and -1 (white).
    """

    metadata = {"render_modes": ["human"], "render_fps": 4}

    def __init__(self, render_mode=None):
        super().__init__()
        self.size = 8  # standard Othello board size

        # Observation space: the full board (8x8), values ∈ {-1, 0, 1}
        self.observation_space = spaces.Box(low=-1, high=1, shape=(self.size, self.size), dtype=np.int8)

        # Action space: choose a cell on the board (0 to 63)
        self.action_space = spaces.Discrete(self.size * self.size)

        self.board = None
        self.current_player = 1  # 1 = black, -1 = white
        self.reset()

    def reset(self, *, seed=None, options=None):
        """
        Reset the environment to the initial Othello setup:
        4 discs in the center in diagonal pattern.
        """
        super().reset(seed=seed)

        # Initialize empty board
        self.board = np.zeros((self.size, self.size), dtype=np.int8)
        mid = self.size // 2
        # Standard starting position
        self.board[mid - 1, mid - 1] = -1
        self.board[mid, mid] = -1
        self.board[mid - 1, mid] = 1
        self.board[mid, mid - 1] = 1

        self.current_player = 1  # Black always starts

        return self.board.copy(), {}

    def step(self, action):
        """
        Take an action:
        - action is an integer (0–63), mapped to board coordinates.
        - if invalid move: penalize with -10 reward.
        - otherwise: place disc, flip opponents, switch player.
        - check if the game is over (no valid moves for either player).
        """
        row, col = divmod(action, self.size)

        # If move invalid → return penalty
        if not self.is_valid_move(row, col, self.current_player):
            return self.board.copy(), -10, False, False, {"invalid": True}

        # Apply move
        self.place_disc(row, col, self.current_player)

        # Switch player
        self.current_player *= -1

        # Check if game is over
        if not self.has_valid_moves(1) and not self.has_valid_moves(-1):
            done = True
            reward = self.get_winner_reward()
        else:
            done = False
            reward = 0

        return self.board.copy(), reward, done, False, {}

    def is_valid_move(self, row, col, player):
        """
        Check if placing a disc at (row, col) is a valid move for `player`.
        Rule: must enclose at least one opponent disc in any direction.
        """
        if self.board[row, col] != 0:
            return False

        # 8 directions to check (orthogonal + diagonal)
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
        """
        Place a disc at (row, col) and flip opponent discs along valid lines.
        """
        self.board[row, col] = player

        # Check all directions for flips
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
                    # Flip captured discs
                    for rr, cc in to_flip:
                        self.board[rr, cc] = player
                    break
                else:
                    break
                r += dr
                c += dc

    def has_valid_moves(self, player):
        """Check if the given player has any valid moves left."""
        for r in range(self.size):
            for c in range(self.size):
                if self.is_valid_move(r, c, player):
                    return True
        return False

    def get_winner_reward(self):
        """
        Count discs and decide winner:
        - Return +1 if current player's opponent wins
        - Return -1 if current player loses
        - Return 0 if tie
        """
        black_count = np.sum(self.board == 1)
        white_count = np.sum(self.board == -1)

        if black_count > white_count:
            return 1 if self.current_player == -1 else -1
        elif white_count > black_count:
            return 1 if self.current_player == 1 else -1
        else:
            return 0

    def render(self):
        """Print the current board state in a human-readable format."""
        print("Current player:", "Black" if self.current_player == 1 else "White")
        for row in self.board:
            print(" ".join(["." if x == 0 else ("B" if x == 1 else "W") for x in row]))
        print()


if __name__ == "__main__":
    # Example: run a short random-play game
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
