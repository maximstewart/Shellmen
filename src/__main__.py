#!/usr/bin/python3

# Python imports
import argparse
import faulthandler
import traceback
from setproctitle import setproctitle

# Lib imports

# Application imports
from __builtins__ import *
from app import Application




if __name__ == "__main__":
    ''' Set process title, get arguments, and create GTK main thread. '''

    try:
        setproctitle(f'{app_name}')
        faulthandler.enable()  # For better debug info

        parser = argparse.ArgumentParser()
        # Add long and short arguments
        parser.add_argument("--theme", "-t", default="default", help="Set the theme. Options [orange, red, purple, green].")
        parser.add_argument("--debug", "-d", default="false", help="Do extra console messaging.")
        parser.add_argument("--trace-debug", "-td", default="false", help="Disable saves, ignore IPC lock, do extra console messaging.")

        # Read arguments (If any...)
        args, unknownargs = parser.parse_known_args()

        if args.debug == "true":
            settings_manager.set_debug(True)

        if args.trace_debug == "true":
            settings_manager.set_trace_debug(True)

        Application(args, unknownargs)
    except Exception as e:
        traceback.print_exc()
        quit()
