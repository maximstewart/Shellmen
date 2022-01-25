# Python imports
import os, signal

# Lib imports
from gi.repository import GLib

# Application imports



class Controller_Data:
    def clear_console(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def call_method(self, _method_name, data = None):
        method_name = str(_method_name)
        method      = getattr(self, method_name, lambda data: f"No valid key passed...\nkey={method_name}\nargs={data}")
        return method(data) if data else method()

    def has_method(self, obj, name):
        return callable(getattr(obj, name, None))

    def setup_controller_data(self, _settings):
        self.settings       = _settings
        self.logger         = self.settings.get_logger()
        self.app_paths      = self.settings.get_app_paths()
        self.favorites_path = self.settings.get_favorites_path()
        self.favorites      = self.settings.get_favorites()

        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, self.tear_down)
