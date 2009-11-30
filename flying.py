import math

import pygame
import numpy as np

def sign(x):
    if x<0:
        return -1
    elif x>0:
        return 1
    else:
        return 0

np.length=lambda(vec): np.sqrt(sum(vec**2))

def countticks(callable):
    """Decorator; Calculates time in pygame ticks since last call 
    and calls 'callable' with ticks count as argument"""
    def wrap(self):
        deltaT = pygame.time.get_ticks() - self.last_ticks
        res = callable(self,deltaT)
        self.last_ticks = pygame.time.get_ticks()
        return res
    return wrap

class Passive(pygame.sprite.DirtySprite):
    """An object that will move passively across the screen"""

    def __init__(self,srcimage,scalefactor=1):
        pygame.sprite.Sprite.__init__(self)
        self.srcimage = srcimage
        self.scalefactor = scalefactor
        srcrect = self.srcimage.get_rect()
        self.rect = srcrect
        self.rect.w = self.rect.h = max(srcrect.w, srcrect.h) * 1.42 / self.scalefactor
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.angle = 0
        self.imagesnum = 48
        self.images = {}
        self.friction =     0.00002 # velocity decrease per milisecond
        self.gravity =      0 #0.00003
        self.velocity = np.array([20.0/1000,20.0/1000]) # pixel per millisecond
        self.angular_velocity = 0 # 2*math.pi/1000 / 2 # radians per millisecond, e.g. 2*2*math.pi/1000 = full rotation in 2 sec
        self.angular_friction =     0.000005
        self.last_ticks = pygame.time.get_ticks() # last time (pygame.time.get_ticks()) when self.tick was called
        self.alpha = 255
        
    def update(self):
        global background
        newpos = self._calcnewpos()
        self.rect = newpos

    @countticks
    def _calcnewpos(self,deltat):
        if abs(self.angular_velocity) > self.angular_friction * deltat:
            self.angular_velocity = sign(self.angular_velocity) * (abs(self.angular_velocity) - self.angular_friction * deltat)
        else:
            self.angular_velocity = 0

        self.last_angle = self.angle
        self.angle += self.angular_velocity * deltat

        # friction:
        if np.length(self.velocity) > self.friction * deltat:
            self.velocity *= (np.length(self.velocity) - self.friction * deltat) / np.length(self.velocity)
        else:
            self.velocity = np.array([0., 0.])

        self.velocity[1] = self.velocity[1] + self.gravity * deltat

        # staying in area / wraparound
        if not self.area.colliderect(self.rect):
            self.rect.x %= self.area.w
            self.rect.y %= self.area.h

        index = int(self.angle / (2 * math.pi) * self.imagesnum)
        if not self.images.has_key(index):
            self.images[index] = pygame.transform.rotozoom(self.srcimage, -self.angle / (2 * math.pi) * 360, 1 / self.scalefactor).convert_alpha()
            self.images[index].set_alpha(self.alpha)

        self.image = self.images[index]
        deltax = [deltat*V for V in self.velocity]

        return self.rect.move(deltax)

class Active(Passive):
    """An object that can be controlled when moving across the screen"""

    def __init__(self,srcimage,scalefactor=1):
        Passive.__init__(self,srcimage,scalefactor)
        self.acceleration = 0.0001 # velocity increase per milisecond when accelerating (Up pressed)
        self.angular_acceleration = 0.00001 # radians per millisecond^2
        self.accelerate = 0 # K_UP pressed
        self.turn = 0 # 0,1,-1 turn direction

    @countticks
    def _calcnewpos(self,deltat):
        if self.turn:
            self.angular_velocity += self.angular_acceleration*self.turn*deltat
        # acceleration:
        if self.accelerate:
            self.velocity += np.array([np.cos(self.angle),np.sin(self.angle)])*self.acceleration*deltat
            # [V+deltat*self.acceleration*projection for V,projection in zip(self.velocity,(math.cos(self.angle),math.sin(self.angle)))]
            #print "velocity: %s" % self.velocity
        return Passive._calcnewpos(self)

class Dropping(Active):
    def __init__(self,srcimage,scalefactor=1):
        Active.__init__(self,srcimage,scalefactor)
        self.droppos = self.newpos = self.rect
        self.drop_interval = 20
        self.pos_delta = 0
        self.droppings = pygame.sprite.OrderedUpdates()

    def _calcnewpos(self):
        self.newpos = Active._calcnewpos(self)
        self.pos_delta = np.length(np.array(self.newpos) - np.array(self.droppos))
        return self.newpos

    def update(self):
        Active.update(self)
        #sys.stdout.write("d: %s\n" % (delta))
        #sys.stdout.flush()
        if self.pos_delta > self.drop_interval:
            self.droppos = self.newpos
            self.drop()
        self.droppings.update()

    def drop(self):
        pass
        
