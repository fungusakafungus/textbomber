#!/usr/bin/env python

import sys
import os

import dissociatedpress

linelen = 78

dp = dissociatedpress.DissociatedPress("cducsu.sqlite")
content = file("scrap/cducsu.txt").read().decode("utf-8")
dp.order = 5
n = dp.order-1
#dp.analyze(content)
line = dp.seed
while 1:
    while len(line) < linelen:
        c = dp.next()
        line += c
        sys.stdout.write(c.encode("utf-8"))
        sys.stdout.flush()
    #sys.stdout.write(line.encode("utf-8"))
    sys.stdin.readline()
    line = ""
    n = (n - 1) % (dp.max_order - 1)
    dp.order = n + 1
    print dp.order
