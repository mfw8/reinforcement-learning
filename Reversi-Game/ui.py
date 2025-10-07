import pygame, sys
import numpy as np
from constants import *
from logic import count_discs

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
