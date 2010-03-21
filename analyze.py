#!/usr/bin/env python

import sys
import os

import dissociatedpress


if len(sys.argv) < 3:
    print "%s db.sqlite textId input.txt" % sys.argv[0]
    print "%s -o db.sqlite" % sys.argv[0]
    sys.exit()
dp = dissociatedpress.DissociatedPress(sys.argv[1],15)
if sys.argv[1] == "-o":
    dp.optimize()
else:
    content = file(sys.argv[3]).read().decode("utf-8")
    dp.analyze(content,sys.argv[2],False)
