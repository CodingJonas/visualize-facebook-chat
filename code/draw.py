import pygame
from pygame import gfxdraw
import colorsys
from math import pow, sin, cos, pi
import numpy as np
import sys

BACKGROUND = (255, 255, 255)
MIN_COLOR_HSV = (240/360,1.0,0.3)
MAX_COLOR_HSV = (150/360,0.0,1.0)

def getColor(r, power=0.5):
    r = pow(r,power)
    new_color_hsv = tuple(x*r+y*(1-r) for x,y in zip(MAX_COLOR_HSV, MIN_COLOR_HSV))
    new_color = colorsys.hsv_to_rgb(*new_color_hsv)
    new_color255 = tuple([x*255 for x in new_color])
    return new_color255

def blur(surface, amt):
    if amt < 1.0:
        raise ValueError("Arg 'amt' must be greater than 1.0, passed in value is %s"%amt)
    scale = 1.0/float(amt)
    surf_size = surface.get_size()
    scale_size = (int(surf_size[0]*scale), int(surf_size[1]*scale))
    surf = pygame.transform.smoothscale(surface, scale_size)
    surf = pygame.transform.smoothscale(surf, surf_size)
    return surf

def remove_holes(surface, background=(0, 0, 0)):
    width, height = surface.get_size()
    array = pygame.surfarray.array3d(surface)
    contains_background = (array == background).all(axis=2)

    neighbours = (0, 1), (0, -1), (1, 0), (-1, 0)

    for row in range(1, height-1):
        for col in range(1, width-1):
            if contains_background[row, col]:
                average = np.zeros(shape=(1, 3), dtype=np.uint16)
                elements = 0
                for y, x in neighbours:
                    if not contains_background[row+y, col+x]:
                        elements += 1
                        average += array[row+y, col+x]
                if elements > 2:  # Only apply average if more than 2 neighbours is not of background color.
                    array[row, col] = average // elements

    return pygame.surfarray.make_surface(array)


def draw_arc(screen, circle_midX, circle_midY, r, min_radius, start, end, color, thickness):
    for x in range(0,thickness):
        gfxdraw.arc(screen, circle_midX, circle_midY, r*thickness+x + min_radius, start, end, color)


def draw_dates_circle(data, sizeX=5000, sizeY=5000, thickness=7, min_radius=1, col_pow=0.2):
    # Set the height and width of the screen
    screen = pygame.Surface((sizeX, sizeY))

    # Draw the image
    # Clear the screen and set the screen background
    screen.fill(BACKGROUND)

    # Real fun part, drawing data
    # Get maximum value
    max_val = 0
    for day in data.values():
        new_val = day[max(day.keys(), key=(lambda k: day[k]))]
        if new_val > max_val:
            max_val = new_val

    if max_val==0:
        print("ERROR: Specified name was never found, did you use the right facebook name?")
        sys.exit()

    # For convenient access to iterate over keys
    keys = list(data.keys())

    # Calculate some parameters
    circle_midX = int(sizeX/2)
    circle_midY = int(sizeY/2)
    parts = len(data[keys[0]])
    delta_minutes = int(1440/parts)

    # Start drawing
    print("Draw image")
    for r in range(0, len(data)):
        for p in range(0,parts):
            start = int(p * 360/(parts))
            end = int((p+1) * 360/(parts))  # maximum 360
            # Set 00:00 to top
            start = (start+270)%360
            end = (end+270)%360
            color_r = data[keys[r]][p*delta_minutes]/max_val
            color = getColor(color_r)
            draw_arc(screen, circle_midX, circle_midY, r, min_radius, start, end, color, thickness)

    # Anti-Aliasing filter
    image = remove_holes(screen, BACKGROUND)
    # Set filtered image
    screen.blit(image, (0,0))
    print("Save Image")
    pygame.image.save(screen, "../images/response_circle.png")



def draw_minutes_circle(data):
    #  screen = pygame.Surface((500,500))

    pygame.init()
    screen = pygame.display.set_mode((1000,1000))

    while True:
        screen.fill(BACKGROUND)

        ## Normalize data
        # Get data into numpy array
        array_data = np.asarray(list(data.values()))

        # normalize data
        array_data = normalize(array_data)

        array_data *= 200
        array_data += 100
        print(array_data)

        length = len(array_data)
        points_circle = [[0,0] for i in range(0,length)]
        points_comp = [[0,0] for i in range(0,length)]

        for i in range(0,length):
            point = [0,0]

            # Map radius on circle points
            point[0] = cos(2*pi * i/length - 0.5*pi) * array_data[i]
            point[1] = sin(2*pi * i/length - 0.5*pi) * array_data[i]
            # Center points
            point[0] += 500
            point[1] += 500
            points_circle[i] = point

            point_comp = [0,0]
            # Map radius on circle points
            point_comp[0] = cos(2*pi * i/length) * 100
            point_comp[1] = sin(2*pi * i/length) * 100
            # Center points
            point_comp[0] += 500
            point_comp[1] += 500
            points_comp[i] = point_comp

        # draw array
        gfxdraw.polygon(screen, points_circle, MIN_COLOR_HSV)
        gfxdraw.polygon(screen, points_comp, MIN_COLOR_HSV)

        screen.blit(screen,(0,0))
        pygame.display.flip() # update the display


def normalize(v):
    max_val = np.amax(v)
    if max_val ==0:
        max_val =np.finfo(v.dtype).eps
    return v/max_val
