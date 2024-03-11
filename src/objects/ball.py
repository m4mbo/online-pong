import pygame
from helpers.constants import *
from logic.collision_handler import *

class Ball():

    def __init__(self, x, y, radius, color):
        self.init_x = x
        self.init_y = y
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.rect = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)
        self.direction = [1, 1]  # Direction of movement in [x, y] coordinates

    def draw(self, win):
        pygame.draw.circle(win, self.color, (self.x, self.y), self.radius)

    def update(self):
        self.x +=  BALL_SPEED * self.direction[0]
        self.y +=  BALL_SPEED * self.direction[1]
        self.rect.center = (self.x, self.y)

    def check_collision(self, p1, p2):
        if self.rect.colliderect(p1.rect) or self.rect.colliderect(p2.rect):
            self.direction[0] *= -1
        elif horizontal_collision(self.rect):
            return True
        elif vertical_collision(self.rect):
            self.direction[1] *= -1
        return False
    
    def resetPos(self):
        self.x = self.init_x
        self.y = self.init_y

