import pygame
import numpy as np
from constants import *
from logic import is_valid_move, place_disc, has_valid_moves, count_discs, get_valid_moves

def calculate_heuristic_scores(board, current_player, valid_moves):
    """
    Calculate heuristic scores for moves based on Othello strategy.
    Returns a dictionary of {(row, col): score}
    """
    scores = {}
    
    # Strategic position values (corners best, edges good, avoid X-squares)
    position_values = np.array([
        [100, -20,  10,   5,   5,  10, -20, 100],
        [-20, -40,  -5,  -5,  -5,  -5, -40, -20],
        [ 10,  -5,   5,   1,   1,   5,  -5,  10],
        [  5,  -5,   1,   1,   1,   1,  -5,   5],
        [  5,  -5,   1,   1,   1,   1,  -5,   5],
        [ 10,  -5,   5,   1,   1,   5,  -5,  10],
        [-20, -40,  -5,  -5,  -5,  -5, -40, -20],
        [100, -20,  10,   5,   5,  10, -20, 100]
    ])
    
    for row, col in valid_moves:
        # Start with positional value
        score = position_values[row, col]
        
        # Simulate the move
        test_board = board.copy()
        place_disc(test_board, row, col, current_player)
        
        # Count discs flipped
        my_discs_after, opp_discs_after = count_discs(test_board)
        my_discs_before, opp_discs_before = count_discs(board)
        
        if current_player == 1:
            flipped = my_discs_after - my_discs_before - 1  # -1 for the placed disc
        else:
            flipped = opp_discs_after - opp_discs_before - 1
        
        # Reward flipping more discs
        score += flipped * 2
        
        # Count opponent's valid moves after this move (mobility)
        opponent_moves = len(get_valid_moves(test_board, -current_player))
        score -= opponent_moves * 3  # Reduce opponent mobility
        
        # Normalize to 1-10 scale
        normalized_score = min(10, max(1, (score + 50) / 20))
        scores[(row, col)] = normalized_score
    
    return scores

def generate_heatmap_surface(screen, board, current_player):
    """
    Generate a heatmap overlay as a surface (called once, then cached).
    Returns a pygame Surface that can be blitted onto the screen.
    """
    valid_moves = get_valid_moves(board, current_player)
    
    if not valid_moves:
        return None
    
    # Create a transparent surface
    heatmap_surface = pygame.Surface((WIDTH, HEIGHT - 60), pygame.SRCALPHA)
    
    # Get move scores using heuristic (no AI)
    scores = calculate_heuristic_scores(board, current_player, valid_moves)
    
    if not scores:
        return None
    
    # Normalize scores to 0-1 range
    score_values = list(scores.values())
    min_score = min(score_values)
    max_score = max(score_values)
    score_range = max_score - min_score if max_score > min_score else 1
    
    # Draw heatmap onto surface
    for (row, col), score in scores.items():
        # Normalize score
        normalized = (score - min_score) / score_range
        
        # Color gradient: Red (bad) -> Yellow (medium) -> Green (good)
        if normalized < 0.5:
            r = 255
            g = int(255 * (normalized * 2))
            b = 0
        else:
            r = int(255 * (1 - (normalized - 0.5) * 2))
            g = 255
            b = 0
        
        color = (r, g, b, 120)  # Add alpha channel
        
        # Draw semi-transparent rectangle
        x = col * CELL_SIZE
        y = row * CELL_SIZE
        
        pygame.draw.rect(heatmap_surface, color, (x, y, CELL_SIZE, CELL_SIZE))
        
        # Draw score text
        font = pygame.font.SysFont(None, 28, bold=True)
        score_text = font.render(f"{score:.1f}", True, BLACK)
        text_rect = score_text.get_rect(center=(x + CELL_SIZE//2, y + CELL_SIZE//2))
        
        # White background for text readability
        bg_rect = text_rect.inflate(10, 6)
        pygame.draw.rect(heatmap_surface, WHITE, bg_rect, border_radius=4)
        pygame.draw.rect(heatmap_surface, BLACK, bg_rect, width=2, border_radius=4)
        
        heatmap_surface.blit(score_text, text_rect)
    
    # Draw legend on the heatmap surface
    draw_legend_on_surface(heatmap_surface)
    
    return heatmap_surface

def draw_legend_on_surface(surface):
    """Draw a color legend for the heatmap on a surface."""
    legend_x = 10
    legend_y = HEIGHT - 160  # Adjust for surface size
    legend_width = 200
    legend_height = 30
    
    # Background
    pygame.draw.rect(surface, WHITE, (legend_x - 5, legend_y - 5, legend_width + 10, legend_height + 40), border_radius=5)
    pygame.draw.rect(surface, BLACK, (legend_x - 5, legend_y - 5, legend_width + 10, legend_height + 40), width=2, border_radius=5)
    
    # Gradient bar
    for i in range(legend_width):
        normalized = i / legend_width
        if normalized < 0.5:
            r = 255
            g = int(255 * (normalized * 2))
            b = 0
        else:
            r = int(255 * (1 - (normalized - 0.5) * 2))
            g = 255
            b = 0
        pygame.draw.line(surface, (r, g, b), (legend_x + i, legend_y), (legend_x + i, legend_y + legend_height))
    
    # Labels
    font = pygame.font.SysFont(None, 20, bold=True)
    bad_text = font.render("Bad", True, BLACK)
    good_text = font.render("Good", True, BLACK)
    surface.blit(bad_text, (legend_x, legend_y + legend_height + 5))
    surface.blit(good_text, (legend_x + legend_width - 35, legend_y + legend_height + 5))