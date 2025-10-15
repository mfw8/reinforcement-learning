import pygame, sys
import numpy as np
from constants import *
from logic import count_discs

def show_analysis(screen, analysis_text):
    """Display AI analysis on screen with scrolling support."""
    screen_width, screen_height = screen.get_size()
    clock = pygame.time.Clock()
    
    # Split text into lines and wrap long lines
    lines = []
    font = pygame.font.SysFont(None, 24)
    max_width = screen_width - 40
    
    for line in analysis_text.split('\n'):
        if not line.strip():
            lines.append("")
            continue
            
        # Wrap long lines
        words = line.split(' ')
        current_line = ""
        for word in words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.rstrip())
                current_line = word + " "
        if current_line:
            lines.append(current_line.rstrip())
    
    rendered_lines = [font.render(line, True, BLACK) for line in lines]
    
    scroll_offset = 0
    line_height = 30
    max_scroll = max(0, len(rendered_lines) * line_height - screen_height + 100)
    
    reading = True
    while reading:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q or event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                    reading = False
                elif event.key == pygame.K_UP:
                    scroll_offset = max(0, scroll_offset - 30)
                elif event.key == pygame.K_DOWN:
                    scroll_offset = min(max_scroll, scroll_offset + 30)
                elif event.key == pygame.K_PAGEUP:
                    scroll_offset = max(0, scroll_offset - 150)
                elif event.key == pygame.K_PAGEDOWN:
                    scroll_offset = min(max_scroll, scroll_offset + 150)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    reading = False
                elif event.button == 4:  # Scroll up
                    scroll_offset = max(0, scroll_offset - 30)
                elif event.button == 5:  # Scroll down
                    scroll_offset = min(max_scroll, scroll_offset + 30)
        
        # Draw background
        screen.fill(GREEN)
        
        # Draw title bar
        title_font = pygame.font.SysFont(None, 32, bold=True)
        title = title_font.render("AI Analysis", True, WHITE)
        pygame.draw.rect(screen, BLACK, (0, 0, screen_width, 50))
        screen.blit(title, (20, 10))
        
        # Draw analysis text
        y_pos = 60 - scroll_offset
        for line in rendered_lines:
            if -50 < y_pos < screen_height - 50:
                screen.blit(line, (20, y_pos))
            y_pos += line_height
        
        # Draw instructions at bottom
        pygame.draw.rect(screen, BLACK, (0, screen_height - 50, screen_width, 50))
        inst_font = pygame.font.SysFont(None, 20)
        instructions = inst_font.render("↑↓ Scroll | PgUp/PgDn Fast Scroll | Space/Click/Q to close", True, WHITE)
        inst_rect = instructions.get_rect(center=(screen_width // 2, screen_height - 25))
        screen.blit(instructions, inst_rect)
        
        # Draw scroll indicator if needed
        if max_scroll > 0:
            scroll_bar_height = max(30, int((screen_height - 100) * (screen_height - 100) / (len(rendered_lines) * line_height)))
            scroll_bar_y = 60 + int((screen_height - 160) * (scroll_offset / max_scroll))
            pygame.draw.rect(screen, GRAY, (screen_width - 15, scroll_bar_y, 10, scroll_bar_height), border_radius=5)
        
        pygame.display.flip()
        clock.tick(30)

def draw_board(screen, board, valid_moves=None):
    screen.fill(GREEN)
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(screen, BLACK, (x, 0), (x, HEIGHT-60))
    for y in range(0, HEIGHT-60, CELL_SIZE):
        pygame.draw.line(screen, BLACK, (0, y), (WIDTH, y))

    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r, c] == 1:
                pygame.draw.circle(screen, BLACK, (c*CELL_SIZE+CELL_SIZE//2, r*CELL_SIZE+CELL_SIZE//2), CELL_SIZE//2 - 5)
            elif board[r, c] == -1:
                pygame.draw.circle(screen, WHITE, (c*CELL_SIZE+CELL_SIZE//2, r*CELL_SIZE+CELL_SIZE//2), CELL_SIZE//2 - 5)

    if valid_moves:
        for r, c in valid_moves:
            pygame.draw.circle(screen, HIGHLIGHT, (c*CELL_SIZE+CELL_SIZE//2, r*CELL_SIZE+CELL_SIZE//2), 15, 3)
    
    font = pygame.font.SysFont(None, 30)
    blacks, whites = count_discs(board)
    score_text = font.render(f"Black: {blacks}  White: {whites}", True, BLACK)
    total_text = font.render(f"Wins → Black: {total_scores['Black']} | White: {total_scores['White']}", True, BLACK)
    screen.blit(score_text, (10, HEIGHT-55))
    screen.blit(total_text, (10, HEIGHT-30))

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

    for i, t in enumerate([text, score_text, total_text, cont_text]):
        screen.blit(t, (50, 100 + i*60))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c: waiting = False
                elif event.key == pygame.K_q:
                    pygame.quit(); sys.exit()