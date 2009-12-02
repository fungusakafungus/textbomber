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

logging.basicConfig(filename="textbomber.log")

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

class TextBomber(flying.Bomber):
    def __init__(self,srcimage,scalefactor=1.0):
        flying.Bomber.__init__(self,srcimage,scalefactor)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)
        self.acceleration = 0.0005 # velocity increase per milisecond when accelerating (Up pressed)
        self.friction =     0.0002 # velocity decrease per milisecond
        self.angular_friction =     0.000020
        self.angular_acceleration = 0.00004 # radians per millisecond^2
        self.dp = dissociatedpress.DissociatedPress("cducsu.sqlite")
        self.dp.order = self.dp.max_order
        self.oldbombs = pygame.sprite.RenderPlain()
        self.drop_interval = 10
        self.imagesnum = 48
        self.bgcolor=(0,100,0)
        self.word = ''

        # Initialise sprites
        self.sprite = pygame.sprite.RenderPlain(self)

        # drop
        self.font = pygame.font.Font(pygame.font.get_default_font(),40)
        #self.font.set_bold(1)
        self.font2 = pygame.font.Font(pygame.font.get_default_font(),35)

    def drop(self):
        char = self.dp.next()

        letterbg = self.font.render(char, 1, (255,255,255),self.bgcolor).convert()
        letterbg.set_colorkey(self.bgcolor)
        #letterbg.set_alpha(254)
        #letter = self.font2.render(char, 1, (255,255,255),self.bgcolor)
        #letter.set_colorkey(self.bgcolor)
        #letterbg.blit(letter, (1,1))
        newsprite = flying.Passive(letterbg,3.1)
        newsprite.alpha = 255
        #newsprite.blendmode = pygame.BLEND_RGBA_ADD
        newsprite.friction = 0.00008
        newsprite.angle = math.atan2(*(self.velocity[::-1]))
        newsprite.rect.x = self.droppos.x
        newsprite.rect.y = self.droppos.y
        #newsprite.velocity = self.velocity/2
        #newsprite.image.set_flags(pygame.SRCALPHA)
        #newsprite.image.blit = verboseBlit
        newsprite.update()
        #background.blit(newsprite.image,self.droppos)
        self.bombs.add(newsprite)

        for victim in self.bombs.sprites():
            if victim.image.get_alpha() < 20:
                victim.image.set_alpha(19)
                self.oldbombs.add(victim)
            else:
                victim.image.set_alpha(victim.image.get_alpha() * 0.98)

    def tick(self):
        global background, screen
        self.oldbombs.draw(background)
        self.oldbombs.draw(screen)
        for d in self.oldbombs:
            d.kill()

        screen.blit(background, self.rect, self.rect)
        for d in self.bombs:
            screen.blit(background, d.rect, d.rect)

        self.sprite.update()
        self.logger.info("starting to update %i bombs" % len(self.bombs))
        self.bombs.update()
        self.logger.info("done updating bombs")
        
        #for d in self.bombs:
        #    screen.blit(d.image,d.rect)
        self.logger.info("starting to blit %i bombs" % len(self.bombs))
        self.bombs.draw(screen)
        self.logger.info("done blitting bombs")
        self.sprite.draw(screen)
        
        pygame.display.flip()

def main():
    global background, screen

    # Initialise screen
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption('Textbomber')

    TIMEREVENT = pygame.USEREVENT+0
    fps = 20

    #pygame.event.set_grab(True)
    pygame.mouse.set_visible(False)
    pygame.time.set_timer(TIMEREVENT, 1000/fps)

    # Initialise ship
    shipimage = load_png('ship.png')
    shipimage = pygame.transform.rotate(shipimage,-90)
    ship = TextBomber(shipimage)
    ship.drop_interval = 5

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
                ship.accelerate=1
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
