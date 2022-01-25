# Python imports
import threading, subprocess
from os.path import isfile
from os import listdir


# Gtk imports
from xdg.DesktopEntry import DesktopEntry

# Application imports
from .mixins import *
from . import Menu, Controller_Data



def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()

    return wrapper


class Controller(ProcessorMixin, Menu, Controller_Data):
    def __init__(self, _settings, args, unknownargs):
        super().__init__(_settings, args)

        self.setup_controller_data(_settings)

        base_options   = ["[  TO MAIN MENU  ]", "Favorites"]
        self.menu_data = self.get_desktop_files_info(self.app_paths)
        query          = ""

        while True:
            try:
                self.clear_console()
                group = self.call_method("main_menu")["group"]
                self.clear_console()

                if "Search..." in group:
                    query = self.call_method("search_menu")["query"]
                if "[ Set Favorites ]" in group:
                    programs_list       = self.get_sub_group("Search...", "")
                    fixed_programs_list = []

                    for program in programs_list:
                        fixed_programs_list.append({'name': program})

                    self.favorites = self.call_method("set_favorites_menu", [fixed_programs_list])["set_faves"]
                    self.save_faves(self.favorites)
                    continue
                if "[ Exit ]" in group:
                    break

                programs_list = ["[  TO MAIN MENU  ]"]
                programs_list += self.get_sub_group(group, query)
                entry     = self.call_method("sub_menu", [group, programs_list])["prog"]

                self.logger.debug(entry)
                if entry not in base_options:
                    self.logger.info(f"[Executing Program] Group: {group} Entry: {entry}")
                    self.execute_program(group, entry)
            except Exception as e:
                self.logger.error(e.printStackTrace())



    def get_desktop_files_info(self, paths):
        menu_objects = {
            "Accessories": [],
            "Multimedia":  [],
            "Graphics":    [],
            "Game":        [],
            "Office":      [],
            "Development": [],
            "Internet":    [],
            "Settings":    [],
            "System":      [],
            "Wine":        [],
            "Other":       []
        }

        for path in paths:
            if not "/opt/" in path:
                self.list_and_update_desktop_iles(path, menu_objects);
            else:
                for folder in listdir(path):
                    try:
                        full_path = f"{path}{folder}/"
                        self.list_and_update_desktop_iles(full_path, menu_objects);
                    except Exception as e:
                        self.logger.debug(e)

        return menu_objects

    def list_and_update_desktop_iles(self, path, menu_objects):
        try:
            for f in listdir(path):
                full_path = f"{path}{f}"
                if isfile(full_path) and f.endswith(".desktop"):
                    xdg_object = DesktopEntry(full_path)
                    hidden     = xdg_object.getHidden()
                    nodisplay  = xdg_object.getNoDisplay()
                    type       = xdg_object.getType()
                    groups     = xdg_object.getCategories()
                    # Do not show those marked as hidden or not to display
                    if hidden or nodisplay:
                        continue

                    if type == "Application" and groups != "":
                        title    = xdg_object.getName()
                        comment  = xdg_object.getComment()
                        # icon     = xdg_object.getIcon()
                        mainExec = xdg_object.getExec()
                        tryExec  = xdg_object.getTryExec()

                        group    = ""
                        if "Accessories" in groups or "Utility" in groups:
                            group = "Accessories"
                        elif "Multimedia" in groups or "Video" in groups or "Audio" in groups:
                            group = "Multimedia"
                        elif "Development" in groups:
                            group = "Development"
                        elif "Game" in groups:
                            group = "Game"
                        elif "Internet" in groups or "Network" in groups:
                            group = "Internet"
                        elif "Graphics" in groups:
                            group = "Graphics"
                        elif "Office" in groups:
                            group = "Office"
                        elif "System" in groups:
                            group = "System"
                        elif "Settings" in groups:
                            group = "Settings"
                        elif "Wine" in groups:
                            group = "Wine"
                        else:
                            group = "Other"

                        menu_objects[group].append( {"title":  title,   "groups": groups,
                                                    "comment": comment, "exec": mainExec,
                                                    "tryExec": tryExec, "fileName": f
                                                })
        except Exception as e:
            self.logger.debug(e)


    def get_sub_group(self, group, query = ""):
        desktop_objects = []
        if "Search..." in group:
            group_keys = self.menu_data.keys()
            for group_key in group_keys:
                for option in self.menu_data[group_key]:
                    keys = option.keys()
                    if "comment" in keys and len(option["comment"]) > 0 :
                        if query.lower() in option["comment"].lower():
                            desktop_objects.append( option["title"] + " || " + option["comment"] )
                    if query.lower() in option["title"].lower() or query.lower() in option["fileName"].lower():
                            desktop_objects.append( option["title"] + " || " + option["fileName"].replace(".desktop", "") )
        elif "Favorites" in group:
            desktop_objects = self.favorites
        else:
            for option in self.menu_data[group]:
                keys = option.keys()
                if "comment" in keys and len(option["comment"]) > 0 :
                    desktop_objects.append( option["title"] + " || " + option["comment"] )
                else:
                    desktop_objects.append( option["title"] + " || " + option["fileName"].replace(".desktop", "") )

        return desktop_objects




    def tear_down(self, widget=None, eve=None):
        quit()

    def get_clipboard_data(self):
        proc    = subprocess.Popen(['xclip','-selection', 'clipboard', '-o'], stdout=subprocess.PIPE)
        retcode = proc.wait()
        data    = proc.stdout.read()
        return data.decode("utf-8").strip()

    def set_clipboard_data(self, data):
        proc = subprocess.Popen(['xclip','-selection','clipboard'], stdin=subprocess.PIPE)
        proc.stdin.write(data)
        proc.stdin.close()
        retcode = proc.wait()
