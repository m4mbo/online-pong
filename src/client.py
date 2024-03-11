import pygame
from objects import paddle
from helpers.constants import *
from network.network import Network

# Initializing important variables
win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Pong Client")
pygame.init()

network = Network(PORT, 'localhost', BUFSIZE)

font = pygame.font.Font(None, 36)   # Font used accross all the game

def redrawWindow(win, p1, p2, b):
    win.fill((0,0,0))
    p1.draw(win)
    p2.draw(win)
    b.draw(win)
    drawScores(p1, p2)
    pygame.display.update()

def drawScores(p1, p2):
    scoreP1_surface = font.render(str(p1.score), True, (255, 255, 255))
    scoreP2_surface = font.render(str(p2.score), True, (255, 255, 255))

    if p1.x == 0:  # If player 1 is on the left
        scoreP1_rect = scoreP1_surface.get_rect(midtop=(win.get_width() // 2 - 100, 20))  
        scoreP2_rect = scoreP2_surface.get_rect(midtop=(win.get_width() // 2 + 100, 20))  
    else:  # If player 1 is on the right
        scoreP1_rect = scoreP1_surface.get_rect(midtop=(win.get_width() // 2 + 100, 20))  
        scoreP2_rect = scoreP2_surface.get_rect(midtop=(win.get_width() // 2 - 100, 20))  

    win.blit(scoreP1_surface, scoreP1_rect)
    win.blit(scoreP2_surface, scoreP2_rect)

def waitingScreen(win):
    win.fill((0,0,0))
    text_surface = font.render("Please wait...", True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=win.get_rect().center)
    win.blit(text_surface, text_rect)
    pygame.display.update()

def handleInput(p1):
    keys = pygame.key.get_pressed()
        
    if keys[pygame.K_DOWN]:
        p1.setDirection(1)
    elif keys[pygame.K_UP]:
        p1.setDirection(-1)
    else:
        p1.setDirection(0)

def interpolateBalls(b, network):
    # Enqueue outgoing packet with client's ball
    network.enqueue_packet(b)
    network.send()
    # Receive opposite client's ball
    data = network.receive()

    if data == "wait":
        main()

    # Interpolate position
    b.x = (b.x + data.x) // 2
    b.y = (b.y + data.y) // 2

    # Interpolate direction
    b.direction = data.direction

def updateScore(p1, b):
    # Checking if ball collided with left or right side of the screen
    if b.rect[0] <= 0 and p1.x != 0:
        p1.increaseScore()
    elif b.rect[0] > 0 and p1.x == 0:
        p1.increaseScore()
    
def displayWinningScreen(win, winner):
    win.fill((0, 0, 0))
    font_large = pygame.font.Font(None, 72)
    text_surface = font_large.render(f"{winner} wins!", True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=win.get_rect().center)
    win.blit(text_surface, text_rect)
    pygame.display.update()
    pygame.time.delay(3000)  # Display winning screen for 3 seconds


def checkWinner(p1,p2):
        # Checking if any player reached 25 points
    if p1.score >= 25:
            if p1.x == 0: 
                winner = "Left"
            else:
                winner = "Right"
            displayWinningScreen(win, winner)
            run = False
            return True
    if p2.score >= 25:
            if p2.x == 0: 
                winner = "Left"
            else:
                winner = "Right"
            displayWinningScreen(win, winner)
            run = False
            return True
    
    return False

def main():

    clock = pygame.time.Clock()

    run = True

    # Starting paddle
    network.enqueue_packet("init_paddle")
    network.send()
    data = network.receive()

    while data == "wait":

        clock.tick(144)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                network.enqueue_packet("end")
                network.close()

        waitingScreen(win)
        network.enqueue_packet("init_paddle")
        network.send()
        data = network.receive()
    
    p1 = data
    p2 = paddle.Paddle(0, 0, PADDLE_WIDTH, PADDLE_HEIGHT, (255,255,255))

    # Starting ball
    network.enqueue_packet("init_ball")
    network.send()
    data = network.receive()

    b = data

    while run:

        clock.tick(144)

        # Enqueue outgoing packet with paddle 1
        network.enqueue_packet(p1)
        network.send()
        # Receive and update opponent's paddle
        data = network.receive()

        if data == "wait":
            main()
        
        p2 = data
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                network.enqueue_packet("end")
                network.send()
                network.close()

        #checking for winner
        if (checkWinner(p1, p2)):
            break

        # Handling input
        handleInput(p1)

        # Updating players position
        p1.update()
        p2.update()
        b.update()

        # Checking collisions and updating score
        if b.check_collision(p1, p2):
            updateScore(p1, b)
            b.resetPos()
                

        # Drawing new frame
        redrawWindow(win, p1, p2, b)

        # Performance test on network
        network.assess()

        # Interpolation to maintain game state consistency
        interpolateBalls(b, network)
        

if __name__ == '__main__':
    main()
