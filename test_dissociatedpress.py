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

    def testSetOrderEarly(self):
        dp = DissociatedPress("tests/data/test.sqlite")
        dp.order = 4

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

    def NOTtestAnalyzeFile(self):
        dp = DissociatedPress("tests/data/test.sqlite")
        contents = file("tests/data/die-linke.txt").read().decode("utf-8")
        dp.analyze(contents)
        for i in range(100):
            dp.next()

    def testIncreaseOrderContinuity(self):
        dp = DissociatedPress("tests/data/test.sqlite")
        dp.analyze("0123456789")
        dp.order = 5
        dp.seed = "01234"
        self.assertEquals(dp.next(),"5")
        dp.order = 6
        self.assertEquals(dp.next(),"6")
        self.assertEquals(dp.next(),"7")

    def testIncreaseOrderContinuity2(self):
        dp = DissociatedPress("tests/data/test.sqlite")
        dp.analyze("0123456789")
        dp.order = 5
        dp.seed = "01234"
        self.assertEquals(dp.next(),"5")
        dp.order = 10
        self.assertEquals(dp.next(),"6")
        self.assertEquals(dp.next(),"7")
        self.assertEquals(dp.next(),"8")
        self.assertEquals(dp.next(),"9")
        self.assertEquals(dp.next(),"0")
        self.assertEquals(dp.next(),"1")

    def testDecreaseOrderContinuity(self):
        dp = DissociatedPress("tests/data/test.sqlite")
        dp.analyze("0123456789")
        dp.order = 5
        dp.seed = "01234"
        self.assertEquals(dp.next(),"5")
        dp.order = 4
        self.assertEquals(dp.next(),"6")

    def testChangeOrderReadOrder(self):
        dp = DissociatedPress("tests/data/test.sqlite")
        dp.analyze("0123456789")
        dp.order = 5
        dp.seed = "01234"
        self.assertEquals(dp.next(),"5")
        dp.order = 10
        for i in xrange(5):
            dp.next()
        self.assertEquals(dp.order,10)

    def testChangeOrderReadOrder2(self):
        dp = DissociatedPress("tests/data/test.sqlite")
        dp.analyze("0123456789")
        dp.order = 10
        dp.seed = "0123456789"
        self.assertEquals(dp.next(),"0")
        dp.order = 3
        for i in xrange(7):
            dp.next()
        self.assertEquals(dp.order,3)

if __name__ == '__main__' :
    #unittest.main(defaultTest="DissociatedPressTests.testBadSeed")
    unittest.main()
