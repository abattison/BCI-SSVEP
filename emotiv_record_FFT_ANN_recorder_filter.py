from pyemotiv import Epoc
from numpy import fft, absolute
from scipy import signal
import pygame, sys, time, json, operator
import pygame.gfxdraw
import pickle
from random import choice
from pygame.locals import *
from collections import deque
import itertools
import os
offset = 0

##############################################
##############################################
##                                          ##
##                                          ##
##   EDIT THESE PARAMETERS BEFORE RUNTIME   ##
##                                          ##
##                                          ##
##############################################
##############################################
##                                          ##
##                                          ##

bot_freq = 8
top_freq = 11
record_freq = bot_freq # valid options are top_freq, bot_freq, "both" ("both" should not be used for training)
fft_size = 128   # how long should our FFT be? (SHOULD BE CONSISTENT ACROSS TRAININGS!)

##                                          ##
##                                          ##
##                                          ##
##############################################
##############################################

# todo add header 4 2 1
# (number of samples, number of inputs, number of outputs)


os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (offset, 0)

pygame.init()
width = 1920 # 1366
height = 1080 - 30# 768 - 30

padding = 300

FPS = 30    # frames per second setting
fps_clock = pygame.time.Clock()

pygame.display.set_mode((width, height), pygame.NOFRAME) #pygame.FULLSCREEN)
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


class Fringe:
    def __init__(self, size):
        self.size  = size
        self.buff = deque()
        self.id = None #TODO: store an ID for which channel this is.
        self.tally8 = 0
        self.tally15 = 0

    def clear(self):
        self.buff.clear()

    def add_sample(self, samples):
        if len(samples) > 0:
            for sample in samples:
                self.buff.append(sample)

        while len(self.buff) > self.size:
            self.buff.popleft()

    def get_input(self):
        return self.buff

    def get_fft(self):
        if len(self.buff) < self.size:
            print "collecting data..."
        # amp = absolute(fft.fft(list(self.buff)))   # this might have to be numpy.absolute()
        ## timestep = 0.125 # times[1]-times[0]    # the distance between the samples (not needed for periodogram)
        # frequencies = fft.fftfreq(len(self.buff), d=timestep)
        perio = signal.periodogram(list(self.buff), fs=128)
        # print "fringe: ",self.buff
        # print "amplitudes: ",amp
        # print "periodogram: ",perio # ,frequencies
        # index, value = max(enumerate(perio[1]), key=operator.itemgetter(1))
        # print "max freq: ", perio[0][index], value

        return perio

        # try:
        #     if perio[1][8] > perio[1][15]: # .item(8)
        #         self.tally8 += 1
        #     else:
        #         self.tally15 += 1
        # except:
        #     pass

        # if perio[0][index] == 8:
        #     self.tally8 += 1
        # if perio[0][index] == 15:
        #     self.tally15 += 1

        # print self.tally8, self.tally15


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
 

bar_height = 150

top_bar = pygame.Rect(0, 0, width, bar_height)
bot_bar = pygame.Rect(0, height-bar_height, width, bar_height)
bars = []

if record_freq == top_freq or record_freq == "both":
    bars.append(Bar(top_bar, top_freq*2))
if record_freq == bot_freq or record_freq == "both":
    bars.append(Bar(bot_bar, bot_freq*2))

fringe_list = []

for x in range(8):
    fringe_list.append(Fringe(fft_size)) # create fringe of FFT size 16


#fringe_list = []

#for x in range(8):
#    fringe_list.append(Fringe(16)) # create fringe of FFT size 16

# fringe = Fringe(fft_size)     # create fringe of FFT size 16
from_file = False
channel_name = 'O1'    # name of the channel to watch

# automagically determine the filename
i = 0
while os.path.exists('{}hz_recording_{}.dat'.format(record_freq, i)):
    i += 1

def main():
  
    recording = {}
    recording['times'] = {}

    data_file = open('{}hz_recording_{}.dat'.format(record_freq, i), 'w')
    raw_file = open('{}hz_recording_{}_raw.csv'.format(record_freq, i), 'w')

    if from_file:
        recording = pickle.load(open('15HzIsolated.dat', 'rb'))
    else:
        epoc = Epoc()

    channel = ['FC3', 'FCZ', 'FC4', 'CP3', 'CPZ', 'CP4', 'PO7', 'PO3', 'POZ', 'PO4', 'PO8', 'AFZ', 'O1', 'O2']
    probe_channel = channel.index(channel_name)   # channel number 1 - 15 from the emotiv device

    input_data = ''
    raw_input_data = ''
    line_number = 1

    for x in range(500):
        draw_screen(bars)

        if not from_file:
            data = epoc.get_raw()  # 14-by-n numpy array containing raw data for AF3 through AF4
            times = epoc.times  # array of interpolated timestamps, just as before

        if(x % 100 == 0):
            print fps_clock.get_fps()

        if from_file:
            # code for loading from file
            fringe.add_sample(recording[frame][probe_channel-1])
            fringe.get_fft()
        else:
            # slows down the frequencies
            for x in range(8):
                fringe = fringe_list[x]
                fringe.add_sample(data[len(channel)-x-1])
                # save samples to the raw data file
                for sample in data[len(channel)-x-1]:
                    raw_input_data += str(sample) + ","
                fft_out = fringe.get_fft()
                # the first part of the periodogram 
                frequency = 0
                for amp in fft_out[1]:
                    if frequency in itertools.chain(range(top_freq-1,top_freq+2) , range(bot_freq-1, bot_freq+2)):
                        input_data += str(amp) + " "
                    frequency += 1

            # pass 
            # fringe.get_input()
            raw_input_data += "\n"
            if record_freq == top_freq:
                input_data += "\n1 -1\n"
            elif record_freq == bot_freq:
                input_data += "\n-1 1\n"

            line_number += 2

            # throw away build up data
            if line_number <= 59:
                input_data = "471 48 2\n" # replace with header for the file

            # data_file.write(input_data)
            
            # print out data every 100th frame
            #     print "["+channel[probe_channel-1]+"] "+str(frequencies)
            #     for i in range(0, len(data)):
            #         print "["+channel[i]+"] "+str(data[i][0])
            
            #for x in range(0, 4):
            #    frequencies[0]

            # recording[frame] = data
            # this is equivelant to:
            # data = epoc.aquire([3,4,5,6,7,8,9,10,11,12,13,14,15,16]) #AF3 through AF4
            # recording['times'][frame] = times

    raw_file.write(raw_input_data)
    data_file.write(input_data)

    # with open('_15HzIsolated_2.dat', 'wb') as handle:
    #     pickle.dump(recording, handle)
    #     handle.close()

    data_file.close()

    # print fringe.tally8, fringe.tally15
    # print recording

main()
     

pygame.display.quit()
