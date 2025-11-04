import pygame
import numpy as np
from constants import *
from logic import is_valid_move, place_disc, has_valid_moves, count_discs, get_valid_moves
import requests
import json

def get_move_scores_from_ai(board, current_player, valid_moves):
    """
    Ask the AI to score each valid move from 1-10.
    Returns a dictionary of {(row, col): score}
    """
    try:
        from explainability_local import board_to_string, OLLAMA_URL, MODEL_NAME, TIMEOUT
        
        board_str = board_to_string(board)
        player_name = "Black" if current_player == 1 else "White"
        
        moves_str = ", ".join([f"({r},{c})" for r, c in valid_moves])
        
        prompt = f"""You are an Othello expert. Rate each move from 1-10 (10=best).

{board_str}

Current Player: {player_name}
Valid Moves: {moves_str}

Rate EACH move on a scale of 1-10. Format your response EXACTLY like this:
(row,col): score
Example:
(2,3): 8
(4,5): 6
(1,2): 4

Rate ALL {len(valid_moves)} moves. Use ONLY this format, no extra text."""

        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "temperature": 0.3,
            "options": {
                "num_predict": 200
            }
        }
        
        print(f"📊 Getting AI scores for {len(valid_moves)} moves...")
        response = requests.post(OLLAMA_URL, json=payload, timeout=TIMEOUT)
        
        if response.status_code == 200:
            result = response.json()
            text = result.get("response", "")
            
            # Parse the response
            scores = {}
            for line in text.split('\n'):
                line = line.strip()
                if '(' in line and ')' in line and ':' in line:
                    try:
                        # Extract (row,col): score
                        coords_part = line.split(':')[0].strip()
                        score_part = line.split(':')[1].strip()
                        
                        # Parse coordinates
                        coords = coords_part.replace('(', '').replace(')', '').split(',')
                        row = int(coords[0].strip())
                        col = int(coords[1].strip())
                        
                        # Parse score
                        score = float(score_part.split()[0])  # Get first number
                        
                        if (row, col) in valid_moves:
                            scores[(row, col)] = score
                    except:
                        continue
            
            print(f"✅ Parsed {len(scores)} move scores")
            return scores
        else:
            print(f"❌ AI request failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error getting move scores: {e}")
        return None

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

def draw_heatmap_overlay(screen, board, current_player):
    """
    Draw a heatmap overlay showing move quality using heuristic scoring.
    Green = good moves, Red = bad moves, Yellow = medium moves
    """
    valid_moves = get_valid_moves(board, current_player)
    
    if not valid_moves:
        return
    
    # Get move scores using heuristic (no AI)
    print("📊 Calculating heuristic move scores...")
    scores = calculate_heuristic_scores(board, current_player, valid_moves)
    
    if not scores:
        return
    
    # Normalize scores to 0-1 range
    score_values = list(scores.values())
    min_score = min(score_values)
    max_score = max(score_values)
    score_range = max_score - min_score if max_score > min_score else 1
    
    # Draw heatmap
    for (row, col), score in scores.items():
        # Normalize score
        normalized = (score - min_score) / score_range
        
        # Color gradient: Red (bad) -> Yellow (medium) -> Green (good)
        if normalized < 0.5:
            # Red to Yellow
            r = 255
            g = int(255 * (normalized * 2))
            b = 0
        else:
            # Yellow to Green
            r = int(255 * (1 - (normalized - 0.5) * 2))
            g = 255
            b = 0
        
        color = (r, g, b)
        
        # Draw semi-transparent rectangle
        x = col * CELL_SIZE
        y = row * CELL_SIZE
        
        # Create surface with alpha
        overlay = pygame.Surface((CELL_SIZE, CELL_SIZE))
        overlay.set_alpha(120)  # Semi-transparent
        overlay.fill(color)
        screen.blit(overlay, (x, y))
        
        # Draw score text
        font = pygame.font.SysFont(None, 28, bold=True)
        score_text = font.render(f"{score:.1f}", True, BLACK)
        text_rect = score_text.get_rect(center=(x + CELL_SIZE//2, y + CELL_SIZE//2))
        
        # White background for text readability
        bg_rect = text_rect.inflate(10, 6)
        pygame.draw.rect(screen, WHITE, bg_rect, border_radius=4)
        pygame.draw.rect(screen, BLACK, bg_rect, width=2, border_radius=4)
        
        screen.blit(score_text, text_rect)
    
    # Draw legend
    draw_legend(screen)
    
    print(f"✅ Heatmap generated for {len(scores)} moves")

def draw_legend(screen):
    """Draw a color legend for the heatmap."""
    legend_x = 10
    legend_y = HEIGHT - 100
    legend_width = 200
    legend_height = 30
    
    # Background
    pygame.draw.rect(screen, WHITE, (legend_x - 5, legend_y - 5, legend_width + 10, legend_height + 40), border_radius=5)
    pygame.draw.rect(screen, BLACK, (legend_x - 5, legend_y - 5, legend_width + 10, legend_height + 40), width=2, border_radius=5)
    
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
        pygame.draw.line(screen, (r, g, b), (legend_x + i, legend_y), (legend_x + i, legend_y + legend_height))
    
    # Labels
    font = pygame.font.SysFont(None, 20, bold=True)
    bad_text = font.render("Bad", True, BLACK)
    good_text = font.render("Good", True, BLACK)
    screen.blit(bad_text, (legend_x, legend_y + legend_height + 5))
    screen.blit(good_text, (legend_x + legend_width - 35, legend_y + legend_height + 5))