import pygame, sys
import numpy as np

pygame.init()

width=600   
height=600
line_width=15
board_rows=3
board_cols=3
circle_rad=60
circle_wid=15
cross_wid=25
space=50

light_blue=(0,205,205)
line_color= (0,102,102)
circle_color=(239,231,200)
cross_color=(66,66,66)
win_message_color = (255, 255, 255) 

screen = pygame.display.set_mode((width,height))
pygame.display.set_caption('Tic Tac Toe')
screen.fill(light_blue)

try:
    font = pygame.font.Font(None, 70)
    small_font = pygame.font.Font(None, 30)
except:
    font = pygame.font.SysFont("monospace", 70) 
    small_font = pygame.font.SysFont("monospace", 30) 

board=np.zeros((board_rows,board_cols))

def draw_line():
    pygame.draw.line(screen,line_color,(0,200),(600,200),line_width)
    pygame.draw.line(screen,line_color,(0,400),(600,400),line_width)
    pygame.draw.line(screen,line_color,(200,0),(200,600),line_width)
    pygame.draw.line(screen,line_color,(400,0),(400,600),line_width)

def draw_figure():
    for row in range(board_rows):
        for col in range(board_cols):
            if board[row][col]==1: 
                pygame.draw.circle(screen,circle_color,(int(col*200 + 100),int(row*200 + 100)),circle_rad,circle_wid)
            elif board[row][col]==2:
                pygame.draw.line(screen,cross_color,(col*200+space,row*200+200-space),(col*200+200-space,row*200+space),cross_wid)
                pygame.draw.line(screen,cross_color,(col*200+space,row*200+space),(col*200+200-space,row*200+200-space),cross_wid)

def mark(row,col,player):
    board[row][col]=player

def available(row,col):
    return board[row][col] == 0
    
def is_board_full():
    return all(board[row][col] != 0 for row in range(board_rows) for col in range(board_cols))

def draw_vertical_line(col,player):
    posX = col*200+100
    color=circle_color if player==1 else cross_color
    pygame.draw.line(screen,color,(posX,15),(posX,height-15),15)

def draw_horizontal_line(row,player):
    posY = row*200+100 
    color=circle_color if player==1 else cross_color
    pygame.draw.line(screen,color,(15,posY),(width-15,posY),15)

def draw_ascending_diagonal(player):
    color=circle_color if player==1 else cross_color
    pygame.draw.line(screen,color,(15,height-15),(width-15,15),15)

def draw_descending_diagonal(player):
    color=circle_color if player==1 else cross_color
    pygame.draw.line(screen,color,(15,15),(width-15,height-15),15)

def draw_win_message(winner=None):
    s = pygame.Surface((width, height), pygame.SRCALPHA)
    s.fill((0, 0, 0, 150))
    screen.blit(s, (0, 0))
    if winner:
        message = f"PLAYER {winner} WIN!"
    else:
        message = "DRAW!" 
    text = font.render(message, True, win_message_color)
    text_rect = text.get_rect(center=(width // 2, height // 2 - 30))
    screen.blit(text, text_rect)

    reset_text = small_font.render("PRESS 'R' TO RESTART", True, win_message_color)
    reset_rect = reset_text.get_rect(center=(width // 2, height // 2 + 30))
    screen.blit(reset_text, reset_rect)

def check_win(player):
    for col in range (board_cols):
        if (board[0][col] == player) and (board[1][col] == player) and (board[2][col] == player):
            draw_vertical_line(col,player)
            draw_figure()
            draw_win_message("O" if player == 1 else "X")
            return True
            
    for row in range (board_rows):
        if (board[row][0] == player) and (board[row][1] == player) and (board[row][2] == player):
            draw_horizontal_line(row,player)
            draw_figure() 
            draw_win_message("O" if player == 1 else "X")
            return True
            
    if (board[2][0]==player) and (board[1][1]==player) and (board[0][2]==player):
        draw_ascending_diagonal(player)
        draw_figure() 
        draw_win_message("O" if player == 1 else "X")
        return True
        
    if (board[0][0]==player) and (board[1][1]==player) and (board[2][2]==player):
        draw_descending_diagonal(player)
        draw_figure() 
        draw_win_message("O" if player == 1 else "X")
        return True
        
    return False

def restart():
    screen.fill(light_blue)
    draw_line()
    global player
    global game_over
    player=2 
    game_over=False
    for row in range(board_rows):
        for col in range(board_cols):
            board[row][col]=0

draw_line()
player = 2
game_over=False

#mainloop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            mouseX = event.pos[0]
            mouseY = event.pos[1]

            clicked_row= int(mouseY//200)
            clicked_col= int(mouseX//200)

            if available (clicked_row,clicked_col):
                if player==1:
                    mark(clicked_row,clicked_col,1)
                    draw_figure()
                    if check_win(player):
                        game_over = True
                    elif is_board_full():
                        game_over = True
                        draw_win_message() 
                    
                    if not game_over:
                         player=2 

                elif player==2: 
                    mark(clicked_row,clicked_col,2)
                    draw_figure()
                    if check_win(player):
                        game_over = True
                    elif is_board_full():
                        game_over = True
                        draw_win_message() 
                        
                    if not game_over:
                        player=1 

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                restart()

    pygame.display.update()
