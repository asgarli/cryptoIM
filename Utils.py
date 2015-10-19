import os
import sys

def errprint(*args):
    for arg in args:
        sys.stderr.write(arg)
    sys.stderr.write(os.linesep)