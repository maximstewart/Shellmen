#!/usr/bin/python3


# Python imports
import argparse, faulthandler, traceback
from setproctitle import setproctitle

import tracemalloc
tracemalloc.start()


# Lib imports


# Application imports
from __init__ import Main


if __name__ == "__main__":
    try:
        # import web_pdb
        # web_pdb.set_trace()

        setproctitle('Shellmen')
        faulthandler.enable()  # For better debug info
        parser = argparse.ArgumentParser()
        # Add long and short arguments
        parser.add_argument("--theme", "-t", default="default", help="The theme to use for the menu. (default, orange, red, purple, green)")

        # Read arguments (If any...)
        args, unknownargs = parser.parse_known_args()

        Main(args, unknownargs)
    except Exception as e:
        traceback.print_exc()
        quit()
