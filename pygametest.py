#!/usr/bin/env python

import os, sys, pygame, math
import numpy as np

os.environ['SDL_VIDEO_CENTERED'] = '1'

pygame.init()

def sign(x):
    if x<0:
        return -1
    elif x>0:
        return 1
    else:
        return 0

np.length=lambda(vec): np.sqrt(sum(vec**2))

class Ship(object):
    angle = 0 # face up
    imagesnum = 48
    images = {}
    scalefactor = 1
    acceleration = 0.0001 # velocity increase per milisecond when accelerating (Up pressed)
    friction =     0.00002 # velocity decrease per milisecond
    gravity =      0.00003
    velocity = np.array([20.0/1000,20.0/1000]) # pixel per millisecond
    angular_velocity = 0 # 2*math.pi/1000 / 2 # radians per millisecond, e.g. 2*2*math.pi/1000 = full rotation in 2 sec
    angular_acceleration = 0.00001 # radians per millisecond^2
    angular_friction =     0.000005
    last_ticks = 0 # last time (pygame.time.get_ticks()) when self.tick was called
    accelerate = 0 # K_UP pressed
    turn = 0 # 0,1,-1 turn direction
    shoot = 0 # don't shoot!
    max_shoot_distance = 100
    shot_surface = pygame.Surface((max_shoot_distance*2,)*2, pygame.SRCALPHA)
    position = np.array([0., 0.])
    last_position = position
    last_line=None
    def __init__(self):
        self.shipimg = pygame.image.load("images/ship.png").convert_alpha()
        self.shipimg = pygame.transform.rotate(self.shipimg,-90)
        self.shiprect = self.shipimg.get_rect()
        self.shiprect.width = self.shiprect.width * 1.42 * self.scalefactor
        self.shiprect.height = self.shiprect.height * 1.42 * self.scalefactor
        self.shiprect.center = (0,0)
        #print self.shiprect

    def move(self,xy):
        """
        xy - (x,y) - offset
        adds xy to position
        """
        #print "moveto %s,%s" % (x,y)
        self.last_position = self.position
        if self.last_line:
            self.last_line[0] = [x1-x2 for x1,x2 in zip(self.last_line[0],xy)]
            self.last_line[1] = [x1-x2 for x1,x2 in zip(self.last_line[1],xy)]
        self.position += np.array(xy)


    def tick(self):
        deltat=pygame.time.get_ticks()-self.last_ticks
        #print "deltat: %i" % deltat

        if self.turn:
            self.angular_velocity += self.angular_acceleration*self.turn*deltat

        if abs(self.angular_velocity)>self.angular_friction*deltat:
            self.angular_velocity = sign(self.angular_velocity)*(abs(self.angular_velocity)-self.angular_friction*deltat)
        else:
            self.angular_velocity = 0

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
        
        self.move([deltat*V for V in self.velocity])
        #print "position: %s" % self.position

        if self.angle > 2 * math.pi:
            self.angle -=2 * math.pi
        elif self.angle < 0:
            self.angle += 2 * math.pi
        if not screen.get_rect().collidepoint(self.position.tolist()):
            self.position %= [background.get_width(), background.get_height()]
            self.last_line=None
        index = int(self.angle / (2*math.pi) * self.imagesnum)
        if not self.images.has_key(index):
            self.images[index] = pygame.transform.rotozoom(self.shipimg, -self.angle / (2*math.pi) * 360, self.scalefactor)
            #self.images[index] = pygame.transform.scale(self.shipimg, (10,10))
            #print self.images[index]
        #self.shiprect.x = self.x - self.shiprect.width/2
        #self.shiprect.y = self.y - self.shiprect.height/2

        self.last_ticks=pygame.time.get_ticks()

    def draw_shot(self):
        global dirty_rects, transparent
        if self.shoot:
            distance=math.sin(self.position[0]*math.pi/width)*\
                     math.sin(self.position[1]*math.pi/height)*self.max_shoot_distance
            shotstart = (self.max_shoot_distance,)*2 # center of shot_surface
            shotend = distance*math.cos(self.angle), distance*math.sin(self.angle)
            shotend = shotstart[0]+shotend[0], shotstart[1]+shotend[1]
            #endofline=self.position[0]+distance*math.cos(self.angle),self.position[1]+distance*math.sin(self.angle)
            if not self.last_line:
                self.last_line=[shotend,self.position.tolist()]

            #dirty = pygame.draw.aalines(background,white,1,(self.position,endofline)+self.last_line,0)
            # aligned = velocity aligned with shot direction, 0..1
            aligned = abs((self.velocity[0]*math.cos(self.angle)+self.velocity[1]*math.sin(self.angle)))/\
                    math.sqrt(sum([x*x for x in self.velocity]))

            #self.max_angular_velocity = max(self.angular_velocity,self.max_angular_velocity)
            max_angular_velocity = 0.01
            color = pygame.Color(*white)
            hue = math.sqrt(sum([x*x for x in self.velocity])) * 10000 % 360 # 0 = red, 0-360
            saturation = math.atan(abs(self.angular_velocity/max_angular_velocity)*math.pi/2.0)*100
            if saturation > 100:
                saturation = 100
            #saturation = 100 - saturation
            value = 20+(1.0-aligned)*80
            alpha = 20
            color.hsva = hue,saturation,value,alpha
            old_shot_surface=self.shot_surface.copy()
            self.shot_surface.fill(transparent)
            pygame.draw.polygon(self.shot_surface,color,[shotstart,shotend]+self.last_line,0)
            copy=old_shot_surface.copy()
            copy.blit(self.shot_surface,(0,0),None,pygame.BLEND_RGB_SUB)
            dirty_rects += (background.blit(copy,self.position.tolist()),)

            self.last_line=[shotend,shotstart]
        else:
            self.last_line=None

    def draw(self):
        global dirty_rects
        self.draw_shot()
        index = int(self.angle / (2*math.pi) * self.imagesnum)
        #pygame.draw.polygon(screen, (255,255,255), (self.x, self.y), 1)
        #pygame.draw.rect(screen, white, self.shiprect, 1)
        #foreground.set_clip(self.shiprect.union(self.last_shiprect))
        dirty=screen.blit(background,(0,0),self.last_shiprect)
        dirty_rects += dirty,
        screen.blit(background,(0,0))
        dirty=screen.blit(self.images[index], self.position.tolist())
        dirty_rects += dirty,self.shiprect.__copy__(),self.last_shiprect.__copy__()
        #screen.blit(foreground,(0,0))

    def clear(self):
        self.last_shiprect = self.shiprect.__copy__()
        #screen.blit(background,(0,0),self.last_shiprect)
        #pygame.draw.fill(screen, black, self.shiprect, 1)


def quit():
    pygame.event.set_grab(False)
    pygame.mouse.set_visible(True)
    sys.exit()

size = width, height = 640, 480
speed = [2, 2]
black = 0, 0, 0
white = 255, 255, 255
transparent = 0, 0, 0, 0
fps = 15

screen = pygame.display.set_mode(size)
print "display info: %s" % pygame.display.Info()
print "screen flags: %x" % screen.get_flags()
#background = screen.copy()
background = screen.convert_alpha()
print "background flags: %x" % background.get_flags()
#foreground = background.convert_alpha()
#print "foreground flags: %x" % foreground.get_flags()
#foreground.fill(transparent)
dirty_rects=[]
ship = Ship()


pygame.TIMEREVENT = pygame.USEREVENT+0

#pygame.event.set_grab(True)
pygame.mouse.set_visible(False)
pygame.time.set_timer(pygame.TIMEREVENT, 1000/fps)

while 1:
    event = pygame.event.wait()
    if event.type == pygame.QUIT: 
        quit()

    elif event.type == pygame.KEYDOWN:
        #print event.key
        if event.key == pygame.K_UP:
            ship.accelerate=1
        elif event.key == pygame.K_LEFT:
            ship.turn=-1.
        elif event.key == pygame.K_RIGHT:
            ship.turn=1.
        elif event.key == pygame.K_SPACE:
            ship.shoot=not ship.shoot
    elif event.type == pygame.KEYUP:
        #print event.key
        if (event.key == pygame.K_q or event.key == pygame.K_ESCAPE): 
            quit()
        elif (event.key == pygame.K_UP):
            ship.accelerate=0
        elif event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
            ship.turn=0
    
#    elif event.type == pygame.MOUSEMOTION:
#        x,y = event.pos
#        ship.moveto(x,y)
#
    elif event.type == pygame.TIMEREVENT:
        ship.clear()
        ship.tick()
        ship.draw()
        pygame.display.update(dirty_rects)
        #pygame.display.flip()
        dirty_rects=[]

### end




