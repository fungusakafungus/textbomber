import unittest
import pygame

import flying
import textbomber

class FlyingTests(unittest.TestCase):
    def setUp(self):
        pygame.init()
        pygame.display.set_mode((100,100))
        self.image = textbomber.load_png("ship.png")

    def tearDown(self):
        pygame.quit()

    def testDecorator(self):
        dro = flying.Dropping(self.image,1)
        dro.update()
