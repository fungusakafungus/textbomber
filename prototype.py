#!/usr/bin/env python

from dissociatedpress import DissociatedPress
from textbomber import Simulation

dbfilename = "programme.sqlite"

def main():
    dp = DissociatedPress(dbfilename)
    sim = Simulation()
    sim.next = dp.next
    sim.start()

import unittest

class DissociatedPressTests(unittest.TestCase):
    def setUp(self):
        DissociatedPress.max_order=10
        DissociatedPress.order=5

    def testInitEmptyDB(self):
        self.failUnless(DissociatedPress("tests/data/empty.sqlite"))

    def testInitNonExistantDB(self):
        self.failIf(DissociatedPress("tests/nonexistant"))

    def testCreate(self):
        dp = DissociatedPress("tests/data/empty.sqlite")
        dp.("")

if __name__ == '__main__' :
    unittest.main()
