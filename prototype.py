#!/usr/bin/env python
# vim: encoding=utf-8

import dissociatedpress as dp
from textbomber import Simulation

dbfilename = "programme.sqlite"

def main():
    dp.__init__(dbfilename)
    sim = Simulation()
    sim.next = dp.next
    sim.start()

import unittest,os

class DissociatedPressTests(unittest.TestCase):
    def setUp(self):
        dp.max_order=10
        dp.order=5
        for path in ["tests/nonexistant"]:
            try:
                os.unlink(path)
            except:
                pass

    def tearDown(self):
        for path in ["tests/nonexistant",
                "tests/data/test.sqlite",
                "tests/data/empty.sqlite"]:
            try: os.unlink(path) 
            except: pass

    def testInitEmptyDB(self):
        self.failUnless(dp.__init__("tests/data/empty.sqlite"))

    def testInitNonExistantDB(self):
        path = "tests/nonexistant"
        self.failUnless(dp.__init__(path))

    def testCreate(self):
        empty = dp.__init__("tests/data/test.sqlite")
        empty.analyze("abcdefghijk")

    def testNext(self):
        dp.__init__("tests/data/test.sqlite")
        dp.analyze("abcdefghijk")
        dp.seed="abcde"
        dp.order=5
        self.assertEquals(dp.next(),"f")

    def testRandomNext(self):
        dp.__init__("tests/data/test.sqlite")
        dp.analyze("abcdeXabcdeYabcdeZxxxxxxxxxxxxxxxx")
        dp.order=5
        res = set()
        for i in range(1000):
            dp.seed="abcde"
            res.add(dp.next())
        self.assertEquals(len(res),3)

    def testNextNext(self):
        dp.__init__("tests/data/test.sqlite")
        dp.analyze("abcdefghijklmnopq")
        dp.seed="abcde"
        dp.order=5
        self.assertEquals(dp.next(),"f")
        self.assertEquals(dp.next(),"g")

    def testCyclicNext(self):
        dp.__init__("tests/data/test.sqlite")
        dp.analyze("abcdefabcd")
        dp.seed="abcde"
        dp.order=5
        res=""
        for i in range(100):
            res+=dp.next()
        self.assertEquals(res,"fabcdabcde"*10)

    def testCyclic2(self):
        dp.__init__("tests/data/test.sqlite")
        dp.analyze("asdglkuzcgvhje")
        dp.order=5
        dp.seed="kuzcg"
        for i in range(100):
            dp.next()

    def testDreadedUnicode(self):
        dp.__init__("tests/data/test.sqlite")
        dp.analyze(u"ÄbcdeXabcdeYabcdeZüxxxxxxxxxxxxxxx")
        dp.seed=u"Yabcd"
        dp.order=5
        for i in range(100):
            dp.next()

    def testBadSeed(self):
        dp.__init__("tests/data/test.sqlite")
        dp.analyze("abcdefghijklmnopq")
        dp.order=5
        dp.seed="xxxx"
        self.assertFail

    def testAnalyzeFile(self):
        dp.__init__("tests/data/big.sqlite")
        contents = file("scrap/cducsu.txt").read()
        dp.analyze(contents)
        dp.seed=u"Einsatz"
        dp.order=5
        for i in range(100):
            dp.next()
        
        

if __name__ == '__main__' :
    #unittest.main(defaultTest="DissociatedPressTests.testNextNext")
    unittest.main()
