
# Python imports
import argparse

# Application imports
from __init__ import Main


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser()
        # Add long and short arguments
        parser.add_argument("--theme", "-t", default="default", help="The theme to use for the menu. (default, orange, red, purple, green)")

        # Read arguments (If any...)
        args = parser.parse_args()
        main = Main(args)
    except Exception as e:
        print( repr(e) )
