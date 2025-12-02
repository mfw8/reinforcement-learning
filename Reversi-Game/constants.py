# --- Settings ---
BOARD_SIZE = 8
CELL_SIZE = 80
BOARD_WIDTH = CELL_SIZE * BOARD_SIZE + 40  # Added 40px for row/column labels
SIDEBAR_WIDTH = 400  # Width for analysis sidebar
WIDTH = BOARD_WIDTH + SIDEBAR_WIDTH
HEIGHT = CELL_SIZE * BOARD_SIZE + 100  # Increased bottom panel for labels
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