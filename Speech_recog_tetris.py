import speech_recognition as sr

import pygame
import random
import sys

from threading import Thread

import time
import re

#################################################################
#Tetris Game on 10 x 20 game board
#Seven shapes_list can be picked from.
#the player places the shape in the desired position
#if an entire row is filled with shapes_list it is removed
#if the shapes_list reach the max height of the game board game over.
#################################################################

#initilise pygame fonts

pygame.font.init()

#GLOBAL GAME VARIABLES

screen_width = 800
screen_height = 700
game_width = 300
game_height = 600
grid_bs = 30

topleft_x = (screen_width - game_width) // 2
topleft_y = screen_height - game_height

next_comand = ""
run = True

#SHAPES
#Representations of the shapses and thier rotations

#   0XX
#   XX0
S = [['.....',
      '.....',
      '..00.',
      '.00..',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

#   XX0
#   0XX
Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

#   X
#   X
#   X
#   X
I = [['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]

#   XX
#   XX
O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

#   X00
#   XXX
J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

#   00X
#   XXX
L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

#   0X0
#   XXX
T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

#list holding shape values defined above
shapes_list = [S, Z, I, O, J, L, T]
#list containing colour values for game peices
shapes_colours = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 128, 0), (0, 0, 255), (165, 0, 165)]

#class definition for game peice
class GamePeice(object):
    rows = 20  # Y cordinate
    columns = 10  # X cordinate
    #init method for peice
    def __init__(self, column, row, shape):
        #y value of peice
        self.y = row
        #x value of peice
        self.x = column
        #shape of peice
        self.shape = shape
        #sets colour of peice
        self.color = shapes_colours[shapes_list.index(shape)]
        #sets rotation of peice
        self.rotation = 0  # number from 0-3

#method for creating game board
def make_grid(locked_locations={}):
    #creates 20 x 10 grid game board
    grid = [[(0,0,0) for x in range(10)] for x in range(20)]
    #sets locked locations for grid
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j,i) in locked_locations:
                c = locked_locations[(j,i)]
                grid[i][j] = c
    return grid

#method to covert shape format
def convert_shape(shape):
    #gets shape formate from shape list
    format = shape.shape[shape.rotation % len(shape.shape)]
    #list containing locations
    locations = []
    #iterates through list containing shape to append new rotated shape
    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                locations.append((shape.x + j, shape.y + i))
    #sets new locations of rotated shape
    for i, pos in enumerate(locations):
        locations[i] = (pos[0] - 2, pos[1] - 4)

    return locations

#method to create new shape at top of game board randomly selected from possible choices
def new_shape():
    #from global shapes_list and colours
    global shapes_list, shapes_colours
    #return a game peice randomly selected from possible shapes_list
    return GamePeice(5, 0, random.choice(shapes_list))

#method to check if player loses
def is_lost(locations):
    #iterates through peice locations to check if any are less than one if so game over
    for pos in locations:
        x, y = pos
        if y < 1:
            return True
    return False

def is_valid(shape, grid):
    accepted_loc = [[(j, i) for j in range(10) if grid[i][j] == (0,0,0)] for i in range(20)]
    accepted_loc = [j for sub in accepted_loc for j in sub]
    formatted = convert_shape(shape)

    for pos in formatted:
        if pos not in accepted_loc:
            if pos[1] > -1:
                return False

    return True

#method to draW Game board grid
def draw_grid(surface, row, col):
    #starting x coordinate
    surfaceX = topleft_x
    #starting y coordinate
    surfaceY = topleft_y
    #nested forloop to draw horizontal and vertical lines using pygames draw line method
    for i in range(row):
        pygame.draw.line(surface, (128,128,128), (surfaceX, surfaceY+ i*30), (surfaceX + game_width, surfaceY + i * 30))  # horizontal lines
        for j in range(col):
            pygame.draw.line(surface, (128,128,128), (surfaceX + j * 30, surfaceY), (surfaceX + j * 30, surfaceY + game_height))  # vertical lines

#draws text to middle
def draw_text(text, size, color, surface):
    #sets fonts
    font = pygame.font.SysFont('freesans', size, bold=True)
    #creates text to display
    display_text = font.render(text, 1, color)
    #places created text on game window
    surface.blit(display_text, (topleft_x + game_width/2 - (display_text.get_width() / 2), topleft_y + game_height/2 - display_text.get_height()/2))


#Draws game window
def draw_window(surface):
    #fills surface with empty blocks
    surface.fill((0,0,0))
    # Sets title to TETRIS
    font = pygame.font.SysFont('freesans', 60)
    text = font.render('TETRIS', 1, (255,255,255))
    #places the title on the game window
    surface.blit(text, (topleft_x + game_width / 2 - (text.get_width() / 2), 30))
    #draws a box for each grid slot to be filled by game peices
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j], (topleft_x + j* 30, topleft_y + i * 30, 30, 30), 0)

    # draw grid and border
    draw_grid(surface, 20, 10)
    pygame.draw.rect(surface, (255, 255, 255), (topleft_x, topleft_y, game_width, game_height), 5)

#checks to see if a row is clear and then shifts above rows down one space
def clear(grid, locked):
    incre = 0
    for i in range(len(grid)-1,-1,-1):
        row = grid[i]
        #checks to see if no empty spaces in row and deletes row if not.
        if (0, 0, 0) not in row:
            incre += 1
            index = i
            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                except:
                    continue
    #corrects locked list after deletions.
    if incre > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < index:
                newKey = (x, y + incre)
                locked[newKey] = locked.pop(key)    

#draws next shape to game board
def draw_shape(shape, surface):
    #sets font and text to render
    font = pygame.font.SysFont('freesans', 30)
    text = font.render('Next Shape', 1, (255,255,255))
    #sets position to render shape
    surfaceX = topleft_x + game_width + 50
    surfaceY = topleft_y + game_height/2 - 100
    #takes the format information from shape object
    format = shape.shape[shape.rotation % len(shape.shape)]
    #draws in blocks according to shape format
    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, shape.color, (surfaceX + j*30, surfaceY + i*30, 30, 30), 0)
    #prints text on game screen
    surface.blit(text, (surfaceX + 10, surfaceY- 30))


    
def main():
    global grid
    global next_comand

    #initilised locked locations list
    locked_locations = {}  # (x,y):(255,0,0)
    grid = make_grid(locked_locations)

    #sets initial flags
    change_piece = False
    global run 
    #gets starting peice
    current_piece = new_shape()
    #gets second peice
    next_piece = new_shape()
    #starts game clock
    clock = pygame.time.Clock()
    #sets fall time to 0
    fall_time = 0
    #Main game loop
    while run:
        #speed that blocks fall
        fall_speed = 0.90
        #sets game grid
        grid = make_grid(locked_locations)
        #speeds up fall time the longer the game gose
        fall_time += clock.get_rawtime()
        #calculates how long since last frame
        clock.tick()

        #code that manages peice falling
        if fall_time/1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not (is_valid(current_piece, grid)) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                quit()
            
            #controls

        control = str(next_comand).lower()

        # regular expresions to give leway to speach recogniser
        if (re.match("^l|.*ft$",control)):
            next_comand = ""
            current_piece.x -= 1
            if not is_valid(current_piece, grid):
                current_piece.x += 1

        elif (re.match("^r|.*ht$",control)):
            next_comand = ""
            current_piece.x += 1
            if not is_valid(current_piece, grid):
                current_piece.x -= 1

        elif (re.match("^t|.*rn$",control)):
            # rotate shape
            next_comand = ""
            current_piece.rotation = current_piece.rotation + 1 % len(current_piece.shape)
            if not is_valid(current_piece, grid):
                current_piece.rotation = current_piece.rotation - 1 % len(current_piece.shape)

        elif (re.match("^d|.*wn$",control)):
            # move shape down
            next_comand = ""
            current_piece.y += 1
            if not is_valid(current_piece, grid):
                current_piece.y -= 1
                

        shape_pos = convert_shape(current_piece)
        

        # add a piece to grid
        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = current_piece.color

        # if a peice hits the ground
        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_locations[p] = current_piece.color
            current_piece = next_piece
            next_piece = new_shape()
            change_piece = False

            # call four times to check for multiple clear rows
            clear(grid, locked_locations)

        draw_window(win)
        draw_shape(next_piece, win)
        pygame.display.update()

        # Check if user lost
        if is_lost(locked_locations):
            run = False

    draw_text("You Lost", 40, (255,255,255), win)
    pygame.display.update()
    pygame.time.delay(2000) 

def main_menu():
    global run
    global next_comand
    while run:
        
        win.fill((0,0,0))
        time.sleep(3)
        draw_text("Say Start to begin.", 40, (255, 255, 255), win)
        
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        if next_comand == "start":
            main()
            
    pygame.quit()

#method to recognise speach and return words spoken
def recog_speech_mic(recog,mic):
    global next_comand
    #takes audio in from mic
    with mic as source:
        recog.adjust_for_ambient_noise(source, duration=0.5)
        audio = recog.listen(source)
    #response structure to return

    #try to interpret user input audio.
    try:
        response = recog.recognize_google(audio)
    except sr.RequestError:
        response = "NONE"
    except sr.UnknownValueError:
        response = "NONE"
        

    
    print(response)
    next_comand = str(response).lower()
        

def speech_loop():
    #initilises recogniser and microphone.
    recog = sr.Recognizer()
    mic = sr.Microphone()

    global next_comand
    global run 

    
    print("IS RUNNING")
    while run:
        t = Thread(target = recog_speech_mic(recog,mic))
        t.start()
        t.join(3)
        

        
  

win = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Tetris')
#thread for main game loop
Thread(target = main_menu).start()  # start game
#thread for speach recognition.
Thread(target =speech_loop).start()
