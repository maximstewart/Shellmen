# Python imports
import traceback

# from pprint import pprint

# Lib imports
from libs.PyInquirer import style_from_dict, Token, prompt, Separator

# Application imports



class Menu:
    """
        The menu class has sub methods that are called per run.
    """

    def __init__(self, args, unknownargs):
        self.theme   = settings_manager.call_method(settings_manager.get_styles(), args.theme)
        base_options = ["[  TO MAIN MENU  ]", "Favorites"]
        body_menu    = [ x.title() for x in settings.filters.__slots__ ]
        GROUPS       = [ "Search...", "Favorites" ] + body_menu + [ "[ Set Favorites ]", "[ Exit ]" ]
        query        = ""
        group        = ""

        self._setup_styling()
        self._setup_signals()
        self._subscribe_to_events()
        self._load_widgets()

        while True:
            try:
                event_system.emit("clear_console")
                results = None
                group   = self.main_menu(GROUPS)["group"]
                event_system.emit("clear_console")

                match group:
                    case "Search...":
                        query   = self.search_menu()["query"]
                        results = event_system.emit_and_await("get_search_results", (query.lower(),))
                    case "Favorites":
                        results = event_system.emit_and_await("get_favorites_results", (group,))
                    case "[ Set Favorites ]":
                        results       = event_system.emit_and_await("get_search_results", ("",))
                        programs_list = [{"name" : "[  TO MAIN MENU  ]"}] + [
                            {"name": prog, "checked": prog in settings.favorites["apps"]} for prog, exec in results
                        ]
                        favorites     = self.set_favorites_menu(programs_list)["set_faves"]
                        settings.favorites["apps"] = favorites
                        continue
                    case "[ Exit ]":
                        break
                    case _:
                        results = event_system.emit_and_await("get_sub_group", (group,))

                programs_list = ["[  TO MAIN MENU  ]"] + [prog for prog, exec in results]
                entry         = self.sub_menu([group, programs_list])["prog"]
                if entry not in base_options:
                    for prog, exec_ops in results:
                        if prog == entry:
                            event_system.emit("execute_program", (exec_ops,))
                            break
            except Exception as e:
                logger.debug(f"Traceback:  {traceback.print_exc()}")
                logger.debug(f"Exception:  {e}")

        settings_manager.save_settings()


    def _setup_styling(self):
        ...

    def _setup_signals(self):
        ...

    def _subscribe_to_events(self):
        ...

    def _load_widgets(self):
        ...


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
        group_list = GROUPS if not _group_list else _group_list
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
