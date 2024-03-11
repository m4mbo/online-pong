from helpers.constants import *

# Where rect is comprised of (x, y, width, height)

def horizontal_collision(rect):
    if rect[0] <= 0 or rect[0] + rect[2] >= WIN_WIDTH:
        return True
    return False

def vertical_collision(rect):
    if rect[1] <= 0 or rect[1] + rect[3] >= WIN_HEIGHT:
        return True
    return False

