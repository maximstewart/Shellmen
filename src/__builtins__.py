# Python imports
import builtins
import threading

# Lib imports

# Application imports
from utils.event_system import EventSystem
from utils.logger import Logger
from utils.settings_manager.manager import SettingsManager


class BuiltinsException(Exception):
    ...


# NOTE: Threads WILL NOT die with parent's destruction.
def threaded_wrapper(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs, daemon=False).start()
    return wrapper

# NOTE: Threads WILL die with parent's destruction.
def daemon_threaded_wrapper(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs, daemon=True).start()
    return wrapper



# NOTE: Just reminding myself we can add to builtins two different ways...
# __builtins__.update({"event_system": Builtins()})
builtins.app_name          = "Shellmen"
builtins.event_system      = EventSystem()
builtins.settings_manager  = SettingsManager()

settings_manager.load_settings()

builtins.settings          = settings_manager.settings
builtins.logger            = Logger(settings_manager.get_home_config_path(), \
                                    _ch_log_lvl=settings.debugging.ch_log_lvl, \
                                    _fh_log_lvl=settings.debugging.fh_log_lvl).get_logger()

builtins.threaded          = threaded_wrapper
builtins.daemon_threaded   = daemon_threaded_wrapper
builtins.event_sleep_time  = 0.05
