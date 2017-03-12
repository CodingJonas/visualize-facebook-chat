import pygame
import os
import sys
from pygame import gfxdraw
import colorsys
from math import pow, sin, cos, pi
import numpy as np
from helper_fun import printProgressBar

BACKGROUND = (255, 255, 255)
MIN_COLOR_HSV = (240/360,1.0,0.3)
MAX_COLOR_HSV = (150/360,0.0,1.0)
COLOR_SURROUNDING = (0,0,255)

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
        printProgressBar (row, height-1, prefix = 'Anti-aliasing')
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

    # Finish drawing the progess bar
    printProgressBar(1, 1, prefix = 'Anti-aliasing')

    return pygame.surfarray.make_surface(array)


def draw_arc(screen, circle_midX, circle_midY, r, min_radius, start, end, color, thickness):
    for x in range(0,thickness):
        gfxdraw.arc(screen, circle_midX, circle_midY, r*thickness+x + min_radius, start, end, color)


def draw_all(data_days, data_min, thickness=5, min_radius=1, col_pow=0.2):
    radius_circle = len(data_days)*thickness
    size_img = radius_circle * 2 * 1.1

    screen = pygame.Surface((size_img,size_img))
    screen.fill(BACKGROUND)

    # Draw respond minutes around big circle
    #  r = size_img
    #  while r > radius_circle:
        #  color = getColor(1-(r-radius_circle)/(size_img-radius_circle))
        #  screen = draw_minutes_on_surface(screen, data_min, radius_circle, r, size_img, color)
        #  r -= 1

    # Draw circle of days on screen
    screen = draw_days_on_surface(screen, data_days, size_img, thickness, min_radius, col_pow)

    # Anti-Aliasing filter
    screen = remove_holes(screen, BACKGROUND)

    screen.blit(screen,(0,0))
    print("Save Image")
    # Get filepath
    cur_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'images', 'response_circle.png'))
    pygame.image.save(screen, cur_path)

def draw_days_on_surface(screen, data, size_img, thickness, min_radius, col_pow):
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
    circle_midX = int(size_img/2)
    circle_midY = int(size_img/2)
    parts = len(data[keys[0]])
    delta_minutes = int(1440/parts)

    # Start drawing
    print("Draw image")
    for r in range(0, len(data)):
        printProgressBar (r, len(data)-1, prefix = 'Raw drawing  ')
        for p in range(0,parts):
            start = int(p * 360/(parts))
            end = int((p+1) * 360/(parts))  # maximum 360
            # Set 00:00 to top
            start = (start+270)%360
            end = (end+270)%360
            color_r = data[keys[r]][p*delta_minutes]/max_val
            color = getColor(color_r)
            draw_arc(screen, circle_midX, circle_midY, r, min_radius, start, end, color, thickness)

    return screen


def draw_minutes_on_surface(screen, data, size_min, size_max, size_img, color):
    # First normalize data
    # Get data into numpy array
    array_data = np.asarray(list(data.values()))

    # normalize data
    array_data = normalize(array_data)

    array_data *= (size_max/2 - size_min)
    array_data += size_min

    length = len(array_data)
    points_circle = [[0,0] for i in range(0,length)]
    points_comp = [[0,0] for i in range(0,length)]

    for i in range(0,length):
        point = [0,0]

        # Map radius on circle points
        point[0] = cos(2*pi * i/length - 0.5*pi) * array_data[i]
        point[1] = sin(2*pi * i/length - 0.5*pi) * array_data[i]
        # Center points
        point[0] += size_img / 2
        point[1] += size_img / 2
        points_circle[i] = point

    # draw array
    gfxdraw.polygon(screen, points_circle, color)

    return screen


def normalize(v):
    max_val = np.amax(v)
    if max_val ==0:
        max_val =np.finfo(v.dtype).eps
    return v/max_val
