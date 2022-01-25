# Python imports
import os, json

# Gtk imports

# Application imports
from . import Logger



class Settings:
    def __init__(self):
        self._SCRIPT_PTH     = os.path.dirname(os.path.realpath(__file__))
        self._USER_HOME      = os.path.expanduser('~')
        self._CONFIG_PATH    = f"{self._USER_HOME}/.config/{app_name.lower()}"
        self._FAVORITES_FILE = f"{self._CONFIG_PATH}/favorites.json"
        self._HOME_APPS      = f"{self._USER_HOME}/.local/share/applications/"
        self._APP_PATHS      = ["/opt/", "/usr/share/applications/", self._HOME_APPS]

        self._logger         = Logger(self._CONFIG_PATH).get_logger()
        self._faves          = []

        if not os.path.exists(self._CONFIG_PATH):
            os.mkdir(self._CONFIG_PATH)
            self._logger     = Logger(self._CONFIG_PATH).get_logger()

        if not os.path.exists(self._FAVORITES_FILE):
            open(self._FAVORITES_FILE, 'a').close()


        with open(self._FAVORITES_FILE) as f:
            try:
                self._faves = json.load(f)
            except Exception as e:
                pass

            f.close()



    def save_faves(self, data = None):
        with open(self._FAVORITES_FILE, 'w') as f:
            json.dump(data, f)
            f.close()



    def get_logger(self):          return self._logger
    def get_favorites_path(self):  return self._FAVORITES_FILE
    def get_app_paths(self):       return self._APP_PATHS
    def get_favorites(self):       return self._faves
