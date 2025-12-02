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

def draw_analysis_sidebar(screen, analysis_text):
    """Draw analysis text in the sidebar on the right side of the board."""
    from constants import BOARD_WIDTH, WIDTH, HEIGHT, SIDEBAR_WIDTH

    # Sidebar background
    sidebar_x = BOARD_WIDTH
    pygame.draw.rect(screen, (240, 240, 240), (sidebar_x, 0, SIDEBAR_WIDTH, HEIGHT))
    pygame.draw.line(screen, BLACK, (sidebar_x, 0), (sidebar_x, HEIGHT), 3)

    # Title
    title_font = pygame.font.SysFont(None, 28, bold=True)
    title = title_font.render("AI Analysis", True, BLACK)
    screen.blit(title, (sidebar_x + 10, 10))

    # Draw divider line under title
    pygame.draw.line(screen, BLACK, (sidebar_x + 10, 40), (WIDTH - 10, 40), 2)

    # Render analysis text
    font = pygame.font.SysFont(None, 20)
    max_width = SIDEBAR_WIDTH - 20
    y_pos = 50

    # Split and wrap text
    lines = []
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

    # Draw text lines
    line_height = 24
    for line in lines:
        if y_pos > HEIGHT - 30:  # Stop if we run out of space
            overflow_font = pygame.font.SysFont(None, 18, italic=True)
            overflow_text = overflow_font.render("(analysis truncated)", True, GRAY)
            screen.blit(overflow_text, (sidebar_x + 10, HEIGHT - 25))
            break

        if line:  # Skip empty lines but preserve spacing
            text_surface = font.render(line, True, BLACK)
            screen.blit(text_surface, (sidebar_x + 10, y_pos))
        y_pos += line_height

    # Instructions at bottom
    inst_font = pygame.font.SysFont(None, 18)
    inst_text = inst_font.render("Press Q to clear analysis", True, GRAY)
    screen.blit(inst_text, (sidebar_x + 10, HEIGHT - 60))

def draw_board(screen, board, valid_moves=None, analysis_text=None):
    """Draw the board with row/column labels and optional analysis sidebar."""
    screen.fill(GREEN)

    # Offset for labels (20px from left/top)
    LABEL_OFFSET = 20
    BOARD_OFFSET = 40

    # Draw column numbers (0-7) at top
    label_font = pygame.font.SysFont(None, 28)
    for c in range(BOARD_SIZE):
        col_label = label_font.render(str(c), True, BLACK)
        col_rect = col_label.get_rect(center=(BOARD_OFFSET + c*CELL_SIZE + CELL_SIZE//2, LABEL_OFFSET))
        screen.blit(col_label, col_rect)

    # Draw row numbers (0-7) on left
    for r in range(BOARD_SIZE):
        row_label = label_font.render(str(r), True, BLACK)
        row_rect = row_label.get_rect(center=(LABEL_OFFSET, BOARD_OFFSET + r*CELL_SIZE + CELL_SIZE//2))
        screen.blit(row_label, row_rect)

    # Draw grid lines
    for x in range(0, CELL_SIZE * BOARD_SIZE + 1, CELL_SIZE):
        pygame.draw.line(screen, BLACK,
                        (BOARD_OFFSET + x, BOARD_OFFSET),
                        (BOARD_OFFSET + x, BOARD_OFFSET + CELL_SIZE * BOARD_SIZE))
    for y in range(0, CELL_SIZE * BOARD_SIZE + 1, CELL_SIZE):
        pygame.draw.line(screen, BLACK,
                        (BOARD_OFFSET, BOARD_OFFSET + y),
                        (BOARD_OFFSET + CELL_SIZE * BOARD_SIZE, BOARD_OFFSET + y))

    # Draw discs
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            center_x = BOARD_OFFSET + c*CELL_SIZE + CELL_SIZE//2
            center_y = BOARD_OFFSET + r*CELL_SIZE + CELL_SIZE//2

            if board[r, c] == 1:
                pygame.draw.circle(screen, BLACK, (center_x, center_y), CELL_SIZE//2 - 5)
            elif board[r, c] == -1:
                pygame.draw.circle(screen, WHITE, (center_x, center_y), CELL_SIZE//2 - 5)

    # Draw valid move highlights
    if valid_moves:
        for r, c in valid_moves:
            center_x = BOARD_OFFSET + c*CELL_SIZE + CELL_SIZE//2
            center_y = BOARD_OFFSET + r*CELL_SIZE + CELL_SIZE//2
            pygame.draw.circle(screen, HIGHLIGHT, (center_x, center_y), 15, 3)

    # Draw score at bottom
    font = pygame.font.SysFont(None, 30)
    blacks, whites = count_discs(board)
    score_text = font.render(f"Black: {blacks}  White: {whites}", True, BLACK)
    total_text = font.render(f"Wins → Black: {total_scores['Black']} | White: {total_scores['White']}", True, BLACK)
    screen.blit(score_text, (10, HEIGHT-80))
    screen.blit(total_text, (10, HEIGHT-50))

    # Draw sidebar with analysis if provided
    if analysis_text:
        draw_analysis_sidebar(screen, analysis_text)

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