#!/usr/bin/env python
# vim: encoding=utf-8

import unittest,os
import logging

logging.basicConfig(filename="dissociatedpress.log")

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

    def testDefaultFilter(self):
        input = """abc ab
abc ab
 
 ab         """
        res = DissociatedPress.defaultFilter(input)
        self.assertEquals(res,"abc ab abc ab ab ")

    def testAnalyze1(self):
        dp = DissociatedPress("tests/nonexistant")
        dp.analyze("abcabcabcabc")

    def testAnalyze2(self):
        dp = DissociatedPress("tests/data/abc.sqlite")
        self.assertRaises(Warning,dp.analyze,"abcabcabcabc")

    def testPrefer0(self):
        dp = DissociatedPress("tests/data/abc2.sqlite")
        preferLogger = logging.getLogger("dissociatedpress.prefer")
        preferLogger.setLevel(logging.info)
        try:
            dp.analyze("abababababababab",0)
        except Warning:
            pass
        try:
            dp.analyze("acacacacacacacac",1)
        except Warning:
            pass
        dp.order = 1
        Bs = 0
        Cs = 0
        line = ""
        dp.prefer = 0
        for i in xrange(100):
            n = dp.next()
            line += n
            if n == 'b':
                Bs += 1
            elif n == 'c':
                Cs += 1
        preferLogger.info(line)
        self.assertTrue(Bs > Cs + 10)

    def testPrefer1(self):
        dp = DissociatedPress("tests/data/abc2.sqlite")
        preferLogger = logging.getLogger("dissociatedpress.prefer")
        preferLogger.setLevel(logging.INFO)
        try:
            dp.analyze("abababababababab",0)
        except Warning:
            pass
        try:
            dp.analyze("acacacacacacacac",1)
        except Warning:
            pass
        dp.order = 1
        Bs = 0
        Cs = 0
        line = ""
        dp.prefer = 1
        for i in xrange(100):
            n = dp.next()
            line += n
            if n == 'b':
                Bs += 1
            elif n == 'c':
                Cs += 1
        preferLogger.info(line)
        self.assertTrue(Bs + 10 < Cs + 10)

    def testManyTextIds(self):
        dp = DissociatedPress("tests/data/abc2.sqlite")
        preferLogger = logging.getLogger("dissociatedpress.prefer")
        preferLogger.setLevel(logging.INFO)
        try:
            dp.analyze("00abababababababab",0)
        except Warning:
            pass
        try:
            dp.analyze("11acacacacacacacac",1)
        except Warning:
            pass
        try:
            dp.analyze("22adadadadadadadad",2)
        except Warning:
            pass
        try:
            dp.analyze("33aeaeaeaeaeaeaeae",3)
        except Warning:
            pass
        dp.order = 1
        line = ""
        for i in xrange(100):
            dp.prefer = i / 5 % 4
            preferLogger.info("set prefer: %s" % dp.prefer)
            n = dp.next()
            line += n
        preferLogger.info(line)

if __name__ == '__main__' :
    #unittest.main(defaultTest="DissociatedPressTests.testBadSeed")
    unittest.main()
