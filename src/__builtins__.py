# Python imports
import builtins

# Lib imports

# Application imports


class Builtins:
    def dummy(self):
        pass



# NOTE: Just reminding myself we can add to builtins two different ways...
# __builtins__.update({"event_system": Builtins()})
builtins.app_name          = "Shellmen"
builtins.debug             = False
builtins.trace_debug       = False
