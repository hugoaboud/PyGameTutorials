#######################################
##  PyGameTutorials - SpaceInvaders  ##
#######################################

# This is a beginner pygame tutorial, implementing a simpliflied version of
# the classic SpaceInvaders game.

# Full tutorial available for free at:
# https://docs.google.com/document/d/1_y1eVRPENI4AIXiS9W5AjKZ-7yUYev09CEfragOZSmM

# GitHub project:
# https://github.com/hugoaboud/PyGameTutorials

import pygame

###################
## Configuration ##
###################

SCREEN = (512,512)

PLAYER_Y = 462
PLAYER_HALF_WIDTH = 10
PLAYER_HALF_HEIGHT = 11

PLAYER_MAX_SPEED = 7
PLAYER_ACCEL = 0.4
PLAYER_DECEL = 0.8

SHOOT_RADIUS = 2
SHOOT_SPEED = 5

ENEMY_HALF_WIDTH = 12
ENEMY_HALF_HEIGHT = 10

LEVEL_X_MOVEMENT = 60
LEVEL_Y_STEP = 15
LEVEL_SPEED = 1

############################
## Game Engine Components ##
############################

## Graphics Engine
# Draw stuff on the screen
class GraphicsEngine:
    def __init__(self, width, height):
        self.screen = pygame.display.set_mode((width, height))

    def Clear(self):
        self.screen.fill((0, 0, 0))

    def Render(self):
        pygame.display.flip()

## Input Handling
# Store the keystates used by the game
# true: pressed, false: not pressed
class InputHandler:
    LEFT = False
    RIGHT = False
    SHOOT = False

    @staticmethod
    def Update(events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    InputHandler.LEFT = True
                elif event.key == pygame.K_RIGHT:
                    InputHandler.RIGHT = True
                elif event.key == pygame.K_SPACE:
                    InputHandler.SHOOT = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    InputHandler.LEFT = False
                elif event.key == pygame.K_RIGHT:
                    InputHandler.RIGHT = False
                elif event.key == pygame.K_SPACE:
                    InputHandler.SHOOT = False

## Collision Handling
# Methods used to evaluate collision between objects
class Collision:
    @staticmethod
    def Point2Rect(x, y, left, right, top, bottom):
        return (x >= left and x <= right and y >= top and y <= bottom)

###################
## Game Elements ##
###################

## A base class for our game objects
# It stores a XY position and a color
class GameObject:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color

## Player (extends GameObject)
# A triangle we can smoothly move left and right which shoots little dots
class Player(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, (255,255,255))
        self.speed = 0
        self.shooting = False
        self.shoots = []

    def Update(self):
        # Left/Right Input (Accelerate/Develerate object)
        if (InputHandler.LEFT):
            if (self.speed > -PLAYER_MAX_SPEED):
                self.speed -= PLAYER_ACCEL
        elif (self.speed < 0):
            self.speed += PLAYER_DECEL
            if (self.speed > 0): self.speed = 0

        if (InputHandler.RIGHT):
            if (self.speed < PLAYER_MAX_SPEED):
                self.speed += PLAYER_ACCEL
        elif (self.speed > 0):
            self.speed -= PLAYER_DECEL
            if (self.speed < 0): self.speed = 0

        # Movement (based on the speed)
        # This acceleration->speed->position method allows for a smooth movement
        self.x += self.speed

        # Clamp Movement
        if (self.x < 0):
            self.x = 0
            self.speed = 0
        elif (self.x > SCREEN[0]):
            self.x = SCREEN[0]
            self.speed = 0

        # Shoot
        if (not self.shooting):
            if (InputHandler.SHOOT):
                self.shooting = True
                self.Shoot()
        else:
            if (not InputHandler.SHOOT):
                self.shooting = False

        # Update Shoots
        for shoot in self.shoots:
            shoot.Update()

    def Shoot(self):
        self.shoots.append(Shoot(self.x,self.y))

    def Render(self, surface):
        # Render Player (triangle)
        pygame.draw.polygon(surface, self.color, [(self.x-PLAYER_HALF_WIDTH,self.y+PLAYER_HALF_HEIGHT),(self.x,self.y-PLAYER_HALF_HEIGHT),(self.x+PLAYER_HALF_WIDTH,self.y+PLAYER_HALF_HEIGHT)])

        # Render Shoots
        for shoot in self.shoots:
            shoot.Render(surface)

## Shoot (extends GameObject)
# A simple dot moving vertically on the screen with constant speed
class Shoot(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, (64,128,255))

    def Update(self):
        self.y -= SHOOT_SPEED

    def Render(self, surface):
        pygame.draw.circle(surface, self.color, (self.x,self.y), SHOOT_RADIUS)

## Enemy (extends GameObject)
# A simple rectangle. The movement is controlled by the Level class.
class Enemy(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, (255,128,64))

    def Render(self, surface):
        pygame.draw.rect(surface, self.color, pygame.Rect(self.x-ENEMY_HALF_WIDTH, self.y-ENEMY_HALF_HEIGHT, 2*ENEMY_HALF_WIDTH, 2*ENEMY_HALF_HEIGHT))

## Level
# Controls a bunch of enemies on the screen
class Level:
    def __init__(self):
        self.enemies = []
        # Create a 12x6 grid of enemies, stored in a "flat" 1D list,
        # not a 2D one, in order to make iteration easier
        for y in range(6):
            self.enemies += [Enemy(64 + x*32, 64 + y*32) for x in range(12)]
        # Movement
        self.tracker = 0
        self.dir = -1

    def Update(self):
        # Move enemies on the screen
        if (self.tracker <= 0):
            self.tracker = LEVEL_X_MOVEMENT
            for enemy in self.enemies:
                enemy.y += LEVEL_Y_STEP
            self.dir *= -1
        else:
            self.tracker -= LEVEL_SPEED
            for enemy in self.enemies:
                enemy.x += LEVEL_SPEED*self.dir

    def Render(self, surface):
        for enemy in self.enemies:
            enemy.Render(surface)

##########
## Game ##
##########

## SpaceInvaders
# This is the game class, it uses all of the above classes to implement
# a simple version of "Space Invaders".
class SpaceInvaders:
    def __init__(self):
        # Game Engine Components
        self.graphics = GraphicsEngine(512, 512);
        self.clock = pygame.time.Clock()

        # Game Elements
        self.player = Player(256,PLAYER_Y)
        self.level = Level()

    def Loop(self):
        # Game Loop
        # Input -> Movement -> Collision -> Game Logic -> Render -> Repeat (if not Game Over)
        gameover = False
        while (not gameover):
            # Input
            events = pygame.event.get()
            for event in events:
                if (event.type == pygame.QUIT):
                    gameover = True
                    break
            InputHandler.Update(events)

            # Update Physics (Movement) and Game Actions (Shooting)
            self.player.Update()
            self.level.Update()

            # Collision
            for enemy in self.level.enemies[:]:
                # enemy rectangle
                left = enemy.x-ENEMY_HALF_WIDTH
                right = enemy.x+ENEMY_HALF_WIDTH
                top = enemy.y-ENEMY_HALF_HEIGHT
                bottom = enemy.y+ENEMY_HALF_HEIGHT
                # enemy crossed ground
                if (bottom >= PLAYER_Y):
                    gameover = True
                    break
                # enemies <-> player
                if (Collision.Point2Rect(self.player.x,self.player.y,left,right,top,bottom)):
                    gameover = True
                    break
                # enemies <-> shoots
                for shoot in self.player.shoots[:]:
                    if (Collision.Point2Rect(shoot.x,shoot.y,left,right,top,bottom)):
                        self.player.shoots.remove(shoot)
                        self.level.enemies.remove(enemy)
                        break

            # Render
            self.graphics.Clear()
            self.player.Render(self.graphics.screen)
            self.level.Render(self.graphics.screen)
            self.graphics.Render()

            # FPS regulation
            self.clock.tick(60)

##########
## Main ##
##########

if __name__ == '__main__':

    game = SpaceInvaders()
    game.Loop()
