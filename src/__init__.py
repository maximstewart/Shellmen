# Python imports
import os, inspect, time

# Lib imports

# Application imports
from utils import Settings
from signal_classes import Controller
from __builtins__ import Builtins




class Main(Builtins):
    def __init__(self, args, unknownargs):
        settings   = Settings()
        controller = Controller(settings, args, unknownargs)

        if not controller:
            raise Exception("Controller exited and doesn't exist...")
