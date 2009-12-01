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
import math
from copy import copy
import functools

import pygame
#import pygame.locals
import numpy as np

import dissociatedpress
import flying

os.environ['SDL_VIDEO_CENTERED'] = '1'


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
    return image

class TextBomber(flying.Dropping):
    def __init__(self,srcimage,scalefactor):
        flying.Dropping.__init__(self,srcimage,scalefactor)
        self.dp = dissociatedpress.DissociatedPress("cducsu.sqlite")
        self.dp.order = self.dp.max_order
        self.olddroppings = pygame.sprite.RenderPlain()

        # Initialise sprites
        self.sprite = pygame.sprite.RenderPlain(self)

    def drop(self):
        char = self.dp.next()
        font = pygame.font.Font(pygame.font.get_default_font(),40)
        #font.set_bold(1)
        font2 = pygame.font.Font(pygame.font.get_default_font(),35)
        letterbg = font.render(char, 1, (0,0,0))
        #letter = font2.render(char, 1, (255,255,255))
        #letterbg.blit(letter, (1,1))
        letterbg = letterbg.convert_alpha()
        newsprite = flying.Passive(letterbg,3.0)
        newsprite.alpha = 101
        newsprite.blendmode = pygame.BLEND_RGBA_ADD
        newsprite.friction = 0.00008
        newsprite.angle = math.atan2(*(self.velocity[::-1]))
        newsprite.rect.x = self.rect.x
        newsprite.rect.y = self.rect.y
        #newsprite.velocity = self.velocity/2
        newsprite.update()
        #newsprite.image.set_flags(pygame.SRCALPHA)
        #newsprite.image.blit = functools.partial(newsprite.image.blit(),
        self.drop_interval = 7
        self.droppings.add(newsprite)
        for victim in self.droppings.sprites():
            if np.length(victim.velocity) < 0.01:
                self.olddroppings.add(victim)
                sys.stdout.flush()

    def tick(self):
        global background, screen
        self.olddroppings.draw(background)
        self.olddroppings.draw(screen)
        for d in self.olddroppings:
            d.kill()

        screen.blit(background, self.rect, self.rect)
        pygame.draw.circle(background, (255,255,255), self.rect.center, self.rect.w/2)
        screen.blit(background, self.rect, self.rect)
        for d in self.droppings:
            screen.blit(background, d.rect, d.rect)

        self.sprite.update()
        self.droppings.update()
        self.droppings.draw(screen)
        self.sprite.draw(screen)
        pygame.display.flip()

def main():
    global background, screen

    # Initialise screen
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    screen.set_alpha(255)
    pygame.display.set_caption('Textbomber')

    TIMEREVENT = pygame.USEREVENT+0
    fps = 30

    #pygame.event.set_grab(True)
    pygame.mouse.set_visible(False)
    pygame.time.set_timer(TIMEREVENT, 1000/fps)

    # Fill background
    background = screen.convert_alpha()
    background.fill((0, 100, 0))

    # Initialise ship
    shipimage = load_png('ship.png')
    shipimage = pygame.transform.rotate(shipimage,-90)
    ship = TextBomber(shipimage,1)
    ship.drop_interval = 15


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
            if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
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
