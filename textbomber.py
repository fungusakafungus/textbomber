#!/usr/bin/python
#
# Tom's Pong
# A simple pong game with realistic physics and AI
# http://www.tomchance.uklinux.net/projects/pong.shtml
#
# Released under the GNU General Public License

VERSION = "0.4"

import sys
import os
import pygame
import math
from pygame.locals import *
import numpy as np

import dissociatedpress

dp = dissociatedpress.DissociatedPress("cducsu.sqlite")

os.environ['SDL_VIDEO_CENTERED'] = '1'

def sign(x):
    if x<0:
        return -1
    elif x>0:
        return 1
    else:
        return 0

np.length=lambda(vec): np.sqrt(sum(vec**2))

def load_png(name):
    """ Load image and return surface and rect"""
    fullname = os.path.join('images', name)
    try:
        image = pygame.image.load(fullname)
        if image.get_alpha is None:
                image = image.convert()
        else:
                image = image.convert_alpha()
    except pygame.error, message:
        print 'Cannot load image:', fullname
        raise SystemExit, message
    return image, image.get_rect()

class Ship(pygame.sprite.Sprite):
    """A ship that will move across the screen
    Returns: ship object
    Functions: update, calcnewpos
    Attributes: area, vector"""

    def __init__(self, (xy), vector):
        pygame.sprite.Sprite.__init__(self)
        self.srcimage, self.rect = load_png('ship.png')
        self.srcimage = pygame.transform.rotate(self.srcimage,-90)
        self.rect.w, self.rect.h = [x*1.42 for x in self.rect.w,self.rect.h]
        self.droppos = self.rect
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.angle = 0
        self.imagesnum = 48
        self.images = {}
        self.scalefactor = 1
        self.acceleration = 0.0001 # velocity increase per milisecond when accelerating (Up pressed)
        self.friction =     0.00002 # velocity decrease per milisecond
        self.gravity =      0 #0.00003
        self.velocity = np.array([20.0/1000,20.0/1000]) # pixel per millisecond
        self.angular_velocity = 0 # 2*math.pi/1000 / 2 # radians per millisecond, e.g. 2*2*math.pi/1000 = full rotation in 2 sec
        self.angular_acceleration = 0.00001 # radians per millisecond^2
        self.angular_friction =     0.000005
        self.accelerate = 0 # K_UP pressed
        self.turn = 0 # 0,1,-1 turn direction
        self.shoot = 0 # don't shoot!
        self.max_shoot_distance = 100
        self.last_ticks = 0 # last time (pygame.time.get_ticks()) when self.tick was called
        self.waygone = 0
        self.kerning = 20

    def update(self):
        global background
        newpos = self.calcnewpos(self.rect)
        self.rect = newpos
        delta = np.length(np.array(newpos)-np.array(self.droppos))
        #sys.stdout.write("d: %s\n" % (delta))
        #sys.stdout.flush()
        if delta > self.kerning:
            self.droppos = newpos
            self.drop()

    def drop(self):
        global dp
        char = dp.next()
        font = pygame.font.Font(pygame.font.get_default_font(),20)
        font.set_bold(1)
        font2 = pygame.font.Font(pygame.font.get_default_font(),17)
        letterbg = font.render(char,1,(0,0,0))
        letter = font2.render (char,1,(255,255,255))
        letterbg.blit(letter,(1,1))
        background.blit(letterbg,self.droppos)
        
    def calcnewpos(self,rect):
        deltat=pygame.time.get_ticks()-self.last_ticks
        #print "deltat: %i" % deltat

        if self.turn:
            self.angular_velocity += self.angular_acceleration*self.turn*deltat

        if abs(self.angular_velocity)>self.angular_friction*deltat:
            self.angular_velocity = sign(self.angular_velocity)*(abs(self.angular_velocity)-self.angular_friction*deltat)
        else:
            self.angular_velocity = 0

        self.last_angle=self.angle
        self.angle += self.angular_velocity*deltat

        # acceleration:
        if self.accelerate:
            self.velocity += np.array([np.cos(self.angle),np.sin(self.angle)])*self.acceleration*deltat
            # [V+deltat*self.acceleration*projection for V,projection in zip(self.velocity,(math.cos(self.angle),math.sin(self.angle)))]
            #print "velocity: %s" % self.velocity
        
        # friction:
        if np.length(self.velocity)>self.friction*deltat:
            self.velocity *= (np.length(self.velocity)-self.friction*deltat)/np.length(self.velocity)
        else:
            self.velocity = np.array([0., 0.])

        self.velocity[1]=self.velocity[1]+self.gravity*deltat

        # staying in area
        if not self.area.colliderect(self.rect):
            self.rect.x %= self.area.w
            self.rect.y %= self.area.h

        index = int(self.angle / (2*math.pi) * self.imagesnum)
        if not self.images.has_key(index):
            self.images[index] = pygame.transform.rotozoom(self.srcimage, -self.angle / (2*math.pi) * 360, self.scalefactor)

        self.image = self.images[index]
        self.last_ticks = pygame.time.get_ticks()
        deltax = [deltat*V for V in self.velocity]

        return self.rect.move(deltax)

def main():
    global background
    # Initialise screen
    pygame.init()
    screen = pygame.display.set_mode((320, 200))
    pygame.display.set_caption('Textbomber')

    TIMEREVENT = USEREVENT+0
    fps = 8

    #pygame.event.set_grab(True)
    pygame.mouse.set_visible(False)
    pygame.time.set_timer(TIMEREVENT, 1000/fps)

    # Fill background
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((0, 100, 0))

    # Initialise ship
    speed = 4
    rand = 0.5
    ship = Ship((0,0),(rand,speed))

    # Initialise sprites
    shipsprite = pygame.sprite.RenderPlain(ship)

    # Blit everything to the screen
    screen.blit(background, (0, 0))
    pygame.display.flip()

    # Event loop
    while 1:
        event = pygame.event.wait()

        if event.type == QUIT: 
            quit()
        elif event.type == KEYDOWN:
            if event.key == K_UP:
                ship.accelerate=1
            elif event.key == K_LEFT:
                ship.turn=-1.
            elif event.key == K_RIGHT:
                ship.turn=1.
            elif event.key == K_SPACE:
                ship.shoot=not ship.shoot
        elif event.type == KEYUP:
            if event.key == K_q or event.key == K_ESCAPE:
                quit()
            elif (event.key == K_UP):
                ship.accelerate=0
            elif event.key == K_LEFT or event.key == K_RIGHT:
                ship.turn=0

        elif event.type == TIMEREVENT:
            screen.blit(background, ship.rect, ship.rect)

            shipsprite.update()
            shipsprite.draw(screen)
            pygame.display.flip()


def quit():
    pygame.event.set_grab(False)
    pygame.mouse.set_visible(True)
    sys.exit()

if __name__ == '__main__': main()
