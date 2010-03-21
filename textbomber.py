#!/usr/bin/python
#
# Textbomber
# Ilya Margolin 2009
#
# Released under the GNU General Public License

VERSION = "0.4"

import sys
import os
import math
import logging

import pygame
#import pygame.locals
import numpy as np

import dissociatedpress
import flying

os.environ['SDL_VIDEO_CENTERED'] = '1'

logging.basicConfig(filename="textbomber.log",level=logging.DEBUG)
#logging.getLogger("LetterBomb").setLevel(logging.WARN)
#logging.getLogger("TextBomber").setLevel(logging.WARN)
#logging.getLogger("dissociatedpress").setLevel(logging.WARN)


def load_png(name):
    """Load image and return surface"""
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
    return image

class LetterBomb(flying.Rotatable):
    def __init__(self,char,angle):
        global font
        self.logger = logging.getLogger(self.__class__.__name__)
        self.bgcolor = (0,0,0)
        self.alpha = 255
        self.min_alpha = 40
        self.fading_rate = 0.002 # part of opacity to loose every update
        self.alive = 1
        #self.font.set_bold(1)
        #self.font2 = pygame.font.Font(pygame.font.get_default_font(),35)
        letter = font.render(char, 1, (255,255,255), self.bgcolor).convert()
        letter.set_colorkey(None)
        letter.set_alpha(None)
        flying.Rotatable.__init__(self,letter,3.0)
        self.angle = angle
        flying.Rotatable.update(self)
        bg = self.image.convert()
        bg.fill(self.bgcolor)
        bg.blit(self.image,bg.get_rect())
        bg.set_colorkey(self.bgcolor)
        bg.set_alpha(self.alpha)
        self.image = bg
        self.logger.debug("colorkey: %s" % (letter.get_colorkey(),))
        self.logger.debug("alpha: %s" % (letter.get_alpha(),))

    def update(self):
        if self.alive:
            self.alpha = self.alpha * (1 - self.fading_rate)
            if self.alpha <= self.min_alpha:
                self.alpha = self.min_alpha
                self.alive = 0
            self.image.set_alpha(self.alpha)
            flying.Rotatable.update(self)

class TextBomber(flying.Bomber):
    def __init__(self,srcimage,scalefactor=1.0):
        flying.Bomber.__init__(self,srcimage,scalefactor)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.acceleration = 0.002 # velocity increase per milisecond when accelerating (Up pressed)
        self.friction =     0.0001 # velocity decrease per milisecond
        self.angular_friction =     0.0000012
        self.angular_acceleration = 0.000002 # radians per millisecond^2
        self.dp = dissociatedpress.DissociatedPress("politik.sqlite")
        self.dp.order = self.dp.max_order
        self.oldbombs = pygame.sprite.RenderPlain()
        self.drop_interval = 10
        self.imagesnum = 48
        self.bgcolor=(0,0,0)
        self.min_velocity = 0.2
        self.min_order = 5
        self.velocity = self.velocity * 10
        self.max_velocity = 0.4

        # Initialise sprites
        self.sprite = pygame.sprite.RenderPlain(self)


    def calcprefer(self):
        max_r = 2
        r = int((math.cos(self.angle) / 2.0 + 0.5) * (max_r + 1))
        self.logger.debug("r: %s" % r)
        return r
    def drop(self):
        self.logger.info("ship velocity: %s" % self.velocity)
        self.dp.prefer = self.calcprefer()
        char = self.dp.next()

        #letter.set_alpha(254)
        #letter = self.font2.render(char, 1, (255,255,255),self.bgcolor)
        #letter.set_colorkey(self.bgcolor)
        #letter.blit(letter, (1,1))
        angle = math.atan2(*(self.velocity[::-1]))
        newbomb = LetterBomb(char,angle)
        newbomb.rect.x = self.droppos.x
        newbomb.rect.y = self.droppos.y
        #newbomb.velocity = self.velocity/2
        #newbomb.image.set_flags(pygame.SRCALPHA)
        #newbomb.image.blit = verboseBlit
        #background.blit(newbomb.image,self.droppos)
        self.bombs.add(newbomb)
        self.bombs.update()

        for victim in self.bombs:
            if not victim.alive:
                self.oldbombs.add(victim)

    def tick(self):
        global background, screen
        self.oldbombs.draw(background)
        for d in self.oldbombs:
            d.kill()

        screen.blit(background, self.rect, self.rect)
        for d in self.bombs:
            screen.blit(background, d.rect, d.rect)

        self.sprite.update()
        
        #for d in self.bombs:
        #    screen.blit(d.image,d.rect)
        self.logger.info("starting to blit %i bombs" % len(self.bombs))
        self.bombs.draw(screen)
        self.logger.info("done blitting bombs")
        self.sprite.draw(screen)
        
        pygame.display.flip()

    def calcvelocity(self):
        smax = self.max_velocity
        smin = self.min_velocity
        vmax = self.dp.max_order
        vmin = 4
        v = self.dp.order
        s = (v - vmin) / (vmax - vmin) * (smax - smin) + smin
        self.velocity = self.velocity * s / np.length(self.velocity)

    def increase_order(self):
        if self.dp.order < self.dp.max_order:
            self.dp.order = self.dp.order + 1
        self.calcvelocity()

    def decrease_order(self):
        if self.dp.order > self.min_order:
            self.dp.order = self.dp.order - 1
        self.calcvelocity()

def main():
    global background, screen, font

    # Initialise screen
    pygame.init()
    screen = pygame.display.set_mode()
    pygame.display.set_caption('Textbomber')

    TIMEREVENT = pygame.USEREVENT+0
    fps = 20

    #pygame.event.set_grab(True)
    pygame.mouse.set_visible(False)
    pygame.time.set_timer(TIMEREVENT, 1000/fps)

    font = pygame.font.Font(pygame.font.get_default_font(),40)

    # Initialise ship
    shipimage = load_png('ship.png')
    shipimage = pygame.transform.rotate(shipimage,-180)
    ship = TextBomber(shipimage)

    # Fill background
    background = screen.convert()
    background.fill(ship.bgcolor)

    # test blit smth to get tranlucency
    #matte = background.convert()
    #transp = pygame.surface.Surface((200,200))
    #transp.fill((255,255,255))
    #transp.set_alpha(100)
    #font = pygame.font.Font(pygame.font.get_default_font(),30)
    #surf2 = font.render(str(transp.get_alpha()),1,(0,0,0,100))
    #matte.blit(transp,(100,100,0,0))
    #matte.blit(surf2,(120,120,0,0))
    #background.blit(transp,transp.get_rect())

    # Blit everything to the screen
    screen.blit(background, (0, 0))
    pygame.display.flip()

    # Event loop
    while 1:
        event = pygame.event.wait()

        if event.type == pygame.QUIT: 
            quit()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                ship.increase_order()
            elif event.key == pygame.K_DOWN:
                ship.decrease_order()
            elif event.key == pygame.K_LEFT:
                ship.turn=-1.
            elif event.key == pygame.K_RIGHT:
                ship.turn=1.

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_f:
                pygame.display.toggle_fullscreen()
            elif event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                quit()
            elif (event.key == pygame.K_UP):
                ship.accelerate=0
            elif event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                ship.turn=0

        elif event.type == TIMEREVENT:
            ship.tick()

def quit():
    pygame.event.set_grab(False)
    pygame.mouse.set_visible(True)
    sys.exit()

if __name__ == '__main__': main()
