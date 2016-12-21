from pyemotiv import Epoc
from numpy import fft
from numpy import absolute
from collections import Counter
import pygame, sys, time, json, operator
import pygame.gfxdraw
import pickle
from random import choice
from pygame.locals import *
import os
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0, 50)

pygame.init()
width = 1440
height = 800
padding = 300

FPS = 60    # frames per second setting
fps_clock = pygame.time.Clock()

# pygame.display.set_mode((width, height), pygame.FULLSCREEN)
icon = pygame.image.load("bci_game.jpg")
pygame.display.set_icon(icon)

surface = pygame.display.set_mode((width, height))
pygame.display.set_caption('BCI Interface Interface')

BLACK = (0, 0, 0)
DARKBG = (39, 40, 34)
WHITE = (255, 255, 255)
PINK = (249, 39, 114)
BLUE = (102, 217, 239)
GREEN = (166, 226, 46)
LIGHT = (203, 232, 107)
ORANGE = (253, 151, 31)
RED = (240, 35, 17)
DRED1 = (108, 0, 17)
DRED2 = (66, 2, 12)
DRED3 = (51, 0, 8)
DORNGE = (87, 27, 12)
DORNGE2 = (187, 101, 23)
DGREEN = (105, 157, 30)
DGREEN2 = (201, 230, 60)
DYELLOW = (224, 189, 36)
YELLOW = (251, 184, 41)
PURPLE = (145, 32, 77)

bci_feedback_horizontal = width/2
bci_marker_width        = 75
bci_marker_height       = 10
target_number           = -5

surface.fill(BLACK)

frame = 0
inv = False
cnt = 0

# define a bar giving it a rectangle to live in
class Bar:
    def __init__(self, rectangle, freq):
        self.b = rectangle
        self.bar_freq = freq
        self.i = False
        self.divisions = 10

    def draw_bar(self):
        if self.i:
            COLOR = WHITE
            _COLOR = BLACK
        else:
            COLOR = BLACK
            _COLOR = WHITE

        if frame % (2*FPS/self.bar_freq) == 0:
            self.i = not self.i

        delta_w = self.b.width/self.divisions
        for x in range(self.divisions):
            r = pygame.Rect(delta_w*x, self.b.top, delta_w, self.b.height)
            if x % 2:
                pygame.draw.rect(surface, COLOR, r)
            else:
                pygame.draw.rect(surface, _COLOR, r)

def draw_screen(bars):
    bar_freq = 8  # Hz flash rate (1 fps = 2 Hz)
    global frame, cnt
    
    surface.fill(DARKBG)

    for b in bars:
        b.draw_bar()

    draw_cursor()
    pygame.display.update()
    fps_clock.tick(FPS)
    frame += 1


def draw_cursor():
    cursor_width = 50  # 100 px cursor
    cursor_height = 2  # 20 px weight
    x = width/2         # start the cursor at half of the screen width (to center).
    x -= cursor_width/2  # adjust x = x - cursor_width/2
    y = height/2        # y component is at half of the window's height (to center).
    y -= cursor_height/2             # this is declaration of cursor_height/2 in px
 
    # 'drawing' the object for the horizontal cursor in the x-axis direction
    cursor_horizontal = pygame.Rect(x, y, cursor_width, cursor_height)
    pygame.draw.rect(surface, WHITE, cursor_horizontal)     # draw object to surface
 
    # repeat for vertical portion of the cursor
    x = width/2
    y = height/2
    # centering
    x -= cursor_height/2
    y -= cursor_width/2
 
    # object constructing
    cursor_vertical = pygame.Rect(x, y, cursor_height, cursor_width)
    pygame.draw.rect(surface, WHITE, cursor_vertical)
 

top_bar = pygame.Rect(0, 0, width, 50)
bot_bar = pygame.Rect(0, height-50, width, 50)
bars = []
bars.append(Bar(top_bar, 8))
bars.append(Bar(bot_bar, 15))
channels = ['FC3', 'FCZ', 'FC4', 'CP3', 'CPZ', 'CP4', 'PO7', 'PO3', 'POZ', 'PO4', 'PO8', 'POZ', 'O1', 'O2']


def main():
 
    epoc = Epoc()
    count = 0
    modulus = 100
    #recording = {}
    #recording['times'] = {}
 
    for x in range(500):
        data = epoc.get_raw()  # 14-by-n numpy array containing raw data for AF3 through AF4
        count += 1
        if count % modulus == 0:
            print '==================\n'
        for x in range(0, len(channels)): 
            times = epoc.times  # array of interpolated timestamps, just as before
            probe_channel = x   # channel number 1 - 15 from the emotiv device
            bad_connection = Counter(data[probe_channel]).most_common(1)[0][0]
            #print bad_connection
            amp = absolute(fft.fft(data[probe_channel]))   # this might have to be numpy.absolute()
            timestep = times[1]-times[0]    # the distance between the samples
            frequencies = fft.fftfreq(amp.size, d=timestep)

            if bad_connection == data[probe_channel][0] and count % modulus == 0:
                print "!!! \t BAD: "+channels[probe_channel]+" (BAD ["+str(bad_connection)+"]: "+str(data[probe_channel])+")"
            elif count % modulus == 0:
                print "["+channels[probe_channel]+"]: \t\t"+str(frequencies)+" (BAD ["+str(bad_connection)+"])"

        # recording[frame] = data
        # this is equivelant to:
        # data = epoc.aquire([3,4,5,6,7,8,9,10,11,12,13,14,15,16]) #AF3 through AF4
        # recording['times'][frame] = times

    '''
    with open('motor.dat', 'wb') as handle:
        pickle.dump(recording, handle)
        handle.close()
    '''

main()
     
# pygame.display.quit()
