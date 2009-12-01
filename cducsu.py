#!/usr/bin/env python

import sys
import os

import dissociatedpress

linelen = 78

dp = dissociatedpress.DissociatedPress("cducsu.sqlite")
content = file("scrap/cducsu.txt").read().decode("utf-8")
#dp.analyze(content)
dp.order = 10
n = dp.order - 1
line = dp.seed
while 1:
    while len(line) < linelen:
        c = dp.next()
        line += c
        sys.stdout.write(c.encode("utf-8"))
        sys.stdout.flush()
    #sys.stdout.write("%s"%dp.order)
    #sys.stdout.write(line.encode("utf-8"))
    try:
        dp.order = int(sys.stdin.readline())
    except (ValueError, RuntimeError), e:
        #print type(e), e
        pass
    line = ""
    n = (n - 1) % (dp.max_order - 3)
    #dp.order = n + 3
