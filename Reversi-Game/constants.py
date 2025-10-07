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
HIGHLIGHT = (255, 255, 100)

# Score tracker
total_scores = {"Black": 0, "White": 0}