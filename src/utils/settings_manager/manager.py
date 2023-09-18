# Python imports
import signal
import json
from os import path
from os import mkdir

# Gtk imports

# Application imports
from ..singleton import Singleton
from ..styles import Styles
from .options.settings import Settings


class MissingConfigError(Exception):
    pass


class SettingsManager(Singleton):
    def __init__(self):
        self._SCRIPT_PTH        = path.dirname(path.realpath(__file__))
        self._USER_HOME         = path.expanduser('~')
        self._USR_PATH          = f"/usr/share/{app_name.lower()}"

        self._USR_CONFIG_FILE   = f"{self._USR_PATH}/settings.json"
        self._HOME_CONFIG_PATH  = f"{self._USER_HOME}/.config/{app_name.lower()}"
        self._CONFIG_FILE       = f"{self._HOME_CONFIG_PATH}/settings.json"

        if not path.exists(self._HOME_CONFIG_PATH):
            mkdir(self._HOME_CONFIG_PATH)


        self.settings: Settings = None
        self._main_window       = None

        self._trace_debug       = False
        self._debug             = False
        self._styles            = Styles()

    def set_main_window(self, window): self._main_window = window

    def get_home_path(self)        -> str: return self._USER_HOME
    def get_home_config_path(self) -> str: return self._HOME_CONFIG_PATH
    def get_main_window(self):             return self._main_window
    def get_styles(self):                  return self._styles
    def get_style(self):                   return self._styles

    def is_trace_debug(self)    -> bool:  return self._trace_debug
    def is_debug(self)          -> bool:  return self._debug

    def set_trace_debug(self, trace_debug: bool):
        self._trace_debug = trace_debug

    def set_debug(self, debug: bool):
        self._debug = debug

    def call_method(self, target_class = None, _method_name = None, data = None):
        method_name = str(_method_name)
        method      = getattr(target_class, method_name, lambda data: f"No valid key passed...\nkey={method_name}\nargs={data}")
        return method(data) if data else method()

    def load_settings(self):
        if not path.exists(self._CONFIG_FILE):
            self.settings = Settings()
            return

        with open(self._CONFIG_FILE) as file:
            data          = json.load(file)
            data["load_defaults"] = False
            self.settings = Settings(**data)

    def save_settings(self):
        with open(self._CONFIG_FILE, 'w') as outfile:
            json.dump(self.settings.as_dict(), outfile, separators=(',', ':'), indent=4)
