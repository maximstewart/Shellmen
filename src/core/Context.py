# Python imports

from __future__ import print_function, unicode_literals
# from pprint import pprint
import json


# Lib imports
from PyInquirer import style_from_dict, Token, prompt, Separator

# Application imports
from .utils import Logger
from .mixins import StylesMixin




GROUPS = [ "Favorites", "Accessories", "Multimedia", "Graphics", "Office",
            "Development", "Internet", "Settings", "System", "Game", "Wine",
            "Other", "Search...", "[ Exit ]"
        ]


class Context(StylesMixin):
    """
        The menu class has sub methods that are called per run.
    """
    def __init__(self, args):
        """
            Construct a new 'Menu' object which pulls in mixins.
            :param args: The terminal passed arguments

            :return: returns nothing
        """
        self.logger = Logger().get_logger("MAIN")
        # Set the theme
        self.theme    = self.call_method(args.theme)
        self.menuData = None


    def mainMenu(self, _grouplist = None):
        """
            Displays the main menu using the defined GROUPS list...
        """
        grouplist = GROUPS if not _grouplist else _grouplist
        menu = {
                'type': 'list',
                'name': 'group',
                'message': '[  MAIN MENU  ]',
                'choices': grouplist
            }

        return prompt(menu, style=self.theme)


    def favoritesMenu(self, _grouplist = None):
        grouplist = GROUPS if not _grouplist else _grouplist
        menu = {
                'type': 'list',
                'name': 'faves',
                'message': '[  Favorites  ]',
                'choices': grouplist
            }


    def subMenu(self, data = ["NO GROUP NAME", "NO PROGRAMS PASSED IN"]):
        group    = data[0]
        progList = data[1]

        menu = {
                'type': 'list',
                'name': 'prog',
                'message': '[  ' + group + '  ]',
                'choices': progList
            }

        return prompt(menu, style=self.theme)


    def searchMenu(self):
        menu = {
            'type': 'input',
            'name': 'query',
            'message': 'Program you\'re looking for: ',
        }

        return prompt(menu, style=self.theme)
