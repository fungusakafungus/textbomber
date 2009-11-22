#!/usr/bin/env python
# vim: encoding=utf-8

import unittest,os

from dissociatedpress import DissociatedPress

class DissociatedPressTests(unittest.TestCase):
    def setUp(self):
        #dp.max_order=10
        #dp.order=5
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
        dp = DissociatedPress("tests/data/empty.sqlite")

    def testInitNonExistantDB(self):
        path = "tests/nonexistant"
        dp = DissociatedPress(path)

    def testCreate(self):
        dp = DissociatedPress("tests/data/test.sqlite")
        dp.analyze("abcdefghijk")

    def testNext(self):
        dp = DissociatedPress("tests/data/test.sqlite")
        dp.analyze("abcdefghijk")
        dp.order=5
        dp.seed="abcde"
        self.assertEquals(dp.next(),"f")

    def testRandomNext(self):
        dp = DissociatedPress("tests/data/test.sqlite")
        dp.analyze("abcdeXabcdeYabcdeZxxxxxxxxxxxxxxxx")
        dp.order=5
        res = set()
        for i in range(1000):
            dp.seed="abcde"
            res.add(dp.next())
        self.assertEquals(len(res),3)

    def testNextNext(self):
        dp = DissociatedPress("tests/data/test.sqlite")
        dp.analyze("abcdefghijklmnopq")
        dp.order=5
        dp.seed="abcde"
        self.assertEquals(dp.next(),"f")
        self.assertEquals(dp.next(),"g")

    def testCyclicNext(self):
        dp = DissociatedPress("tests/data/test.sqlite")
        dp.analyze("abcdefabcd")
        dp.order=5
        dp.seed="abcde"
        res=""
        for i in range(100):
            res+=dp.next()
        self.assertEquals(res,"fabcdabcde"*10)

    def testCyclic2(self):
        dp = DissociatedPress("tests/data/test.sqlite")
        dp.analyze("asdglkuzcgvhje")
        dp.order=5
        dp.seed="kuzcg"
        for i in range(100):
            dp.next()

    def testDreadedUnicode(self):
        dp = DissociatedPress("tests/data/test.sqlite")
        dp.analyze(u"ÄbcdeXabcdeYabcdeZüxxxxxxxxxxxxxxx")
        dp.order=5
        dp.seed=u"Yabcd"
        for i in range(100):
            dp.next()

    def testBadSeed(self):
        dp = DissociatedPress("tests/data/test.sqlite")
        dp.analyze("abcdefghijklmnopq")
        dp.order=5
        try:
            dp.seed="xxxx"
            raise unittest.AssertionError
        except RuntimeError:
            pass

    def testAnalyzeFile(self):
        dp = DissociatedPress("tests/data/big.sqlite")
        contents = file("scrap/cducsu.txt").read()
        #dp.analyze(contents)
        for i in range(100):
            dp.next()

    def testIncreaseOrder(self):
        pass

if __name__ == '__main__' :
    unittest.main(defaultTest="DissociatedPressTests.testBadSeed")
    #unittest.main()
