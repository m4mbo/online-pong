import pygame
from helpers.constants import *
from logic.collision_handler import vertical_collision

class Paddle():

    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.rect = (x, y, width, height)
        self.direction = 0
        self.score = 0
    
    def draw(self, win):
        pygame.draw.rect(win, self.color, self.rect)

    def update(self):
        new_y = self.y + (self.direction * PADDLE_SPEED)
        new_rect = (self.x, new_y, self.width, self.height)
        if not vertical_collision(new_rect):
            self.y = new_y
            self.rect = new_rect
        
    def setDirection(self, direction):
        self.direction = direction

    def increaseScore(self):
        self.score += 1


