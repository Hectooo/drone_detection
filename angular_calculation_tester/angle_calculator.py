import pygame
import sys
import argparse
import math

from functions import *
from Focuser import *

pygame.init()

WIDTH = 1023
HEIGHT = 1023

parser = argparse.ArgumentParser(description='Process some arguments.')
    
# Define the expected arguments and their defaults
parser.add_argument('--img', type=str, default='images/img1.jpg', help='Path to the image file')
parser.add_argument('--ptz', action='store_true', help='PTZ boolean flag')
parser.add_argument('--bus', type=int, default=7, help='Bus integer value')

# Parse the arguments
args, unknown = parser.parse_known_args()
    
# Check for unrecognized arguments
if unknown:
    print("USAGE: script.py [--img <img_file_path>] [--ptz <boolean>] [--bus <int>]")
    print("Unrecognized arguments found:", unknown)
    sys.exit(1)


TEST_PTZ_SUPPORT = args.ptz
image = pygame.image.load(args.img)
bus = args.bus

# Load the structure to manipulate the PTZ camera
focuser = Focuser(bus)
# Set the PTZ camera to Adjust Mode to be able to move it
focuser.set(Focuser.OPT_MODE,0x0001)

# The two following variable allow a slower manipulation of the PTZ Camera. 
CYCLE_LOOP = 3
CYCLE = 0

image = pygame.transform.scale(image, (WIDTH,HEIGHT))
clock = pygame.time.Clock()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('angle simulation')


# Convert the angle coordinate to fit the PTZ camera spatial configuration, then send the result to the PTZ camera
def angle2PTZ(focuser, elevation, azimut):
    X_angle, Y_angle = azimut, elevation
    if azimut > 0:
        Y_angle = 180 - elevation
        X_angle = 180 - azimut
    else:
        X_angle = azimut * -1
        
    #print("X_angle : {:.2f}, Y_angle : {:.2f}".format(X_angle, Y_angle))
    #print("azimut : {:.2f}, elevation : {:.2f}".format(azimut, elevation))
    focuser.set(Focuser.OPT_MOTOR_X, int(X_angle))
    focuser.set(Focuser.OPT_MOTOR_Y, int(Y_angle))

    
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False

    # display image and the x,y axis in red
    screen.blit(image, (0, 0))
    pygame.draw.line(screen, (255, 0, 0), (WIDTH//2, 0), (WIDTH//2, HEIGHT), 3)
    pygame.draw.line(screen, (255, 0, 0), (0, HEIGHT//2), (WIDTH, HEIGHT//2), 3)

    # get cursor coordinates and draw a blue circle to represent it
    cursor_x, cursor_y = pygame.mouse.get_pos()
    pygame.draw.circle(screen, (0, 0, 255), (cursor_x, cursor_y), 3)

    # get elevation angle according to the cursor position
    elevation = get_elevation(cursor_x, cursor_y, WIDTH, HEIGHT)
    # get hour angle according to the cursor position
    azimut = get_azimut(cursor_x, cursor_y, WIDTH, HEIGHT)
    # Print the result
    print("hour angle : {:.2f}, elevation : {:.2f}".format(azimut, elevation))

    # In order to have more controlled camera movement, the communication delay has been increased 
    CYCLE += 1
    if CYCLE >= CYCLE_LOOP:
        CYCLE = 0
        if TEST_PTZ_SUPPORT:
            angle2PTZ(focuser, elevation, azimut)
        
        
    pygame.display.flip()
    clock.tick(24)

pygame.quit()
sys.exit()


    
