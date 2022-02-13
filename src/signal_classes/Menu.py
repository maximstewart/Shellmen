# Python imports

from __future__ import print_function, unicode_literals
# from pprint import pprint
import json


# Lib imports
from PyInquirer import style_from_dict, Token, prompt, Separator

# Application imports
from .mixins import StylesMixin




GROUPS = [ "Search...", "Favorites", "Accessories", "Multimedia", "Graphics", "Office",
            "Development", "Internet", "Settings", "System", "Game", "Wine",
            "Other", "[ Set Favorites ]", "[ Exit ]"
        ]


class Menu(StylesMixin):
    """
        The menu class has sub methods that are called per run.
    """
    def __init__(self, settings, args):
        """
            Construct a new 'Menu' object which pulls in mixins.
            :param args: The terminal passed arguments

            :return: returns nothing
        """
        self.logger    = settings.get_logger()
        self.theme     = self.call_method(args.theme)


    def main_menu(self, _group_list = None):
        """
            Displays the main menu using the defined GROUPS list...
        """
        group_list = GROUPS if not _group_list else _group_list
        menu = {
                'type': 'list',
                'name': 'group',
                'message': '[  MAIN MENU  ]',
                'choices': group_list
            }

        return prompt(menu, style=self.theme)


    def set_favorites_menu(self, _group_list = None):
        GROUPS     = [{'name': '[  TO MAIN MENU  ]'}, {'name': 'This is a stub method for Favorites...'}]
        group_list = GROUPS if not _group_list[0] else _group_list[0]
        menu = {
            'type': 'checkbox',
            'qmark': '>',
            'message': 'Select Favorites',
            'name': 'set_faves',
            'choices': group_list
        }

        return prompt(menu, style=self.theme)


    def sub_menu(self, data = ["NO GROUP NAME", "NO PROGRAMS PASSED IN"]):
        group     = data[0]
        prog_list = data[1]

        menu = {
                'type': 'list',
                'name': 'prog',
                'message': f'[  {group}  ]',
                'choices': prog_list
            }

        return prompt(menu, style=self.theme)


    def search_menu(self):
        menu = {
            'type': 'input',
            'name': 'query',
            'message': 'Program you\'re looking for: ',
        }

        return prompt(menu, style=self.theme)
