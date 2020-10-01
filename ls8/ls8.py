#!/usr/bin/env python3

"""Main."""

import sys
from cpu import *

if len(sys.argv) == 1:
    print("Usage: python3 ls8.py 'enter valid filename'")

else:
    cpu = CPU()

    cpu.load(sys.argv[1])
    cpu.run()
