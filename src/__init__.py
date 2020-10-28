# Python imports
import subprocess
import os

from os.path import isdir, isfile, join
from os import listdir

# Gtk imports
from xdg.DesktopEntry import DesktopEntry

# Application imports
from core import Context


class Main(Context):
    """
        This is the start class called from "__main__"
    """
    def __init__(self, args):
        """
            Initialize it all...
        """
        super().__init__(args)
        HOME_APPS     = os.path.expanduser('~') + "/.local/share/applications/"
        paths         = ["/opt/", "/usr/share/applications/", HOME_APPS]
        baseOptions   = ["[  TO MAIN MENU  ]", "Favorites"]
        self.menuData = self.getDesktopFilesInfo(paths)
        query         = ""

        while True:
            try:
                self.clear()
                group = self.call_method("mainMenu")["group"]
                self.clear()

                if "Search..." in group:
                    query = self.call_method("searchMenu")["query"]
                if "Favorites" in group:
                    query = self.call_method("favoritesMenu")["faves"]
                    continue
                if "[ Exit ]" in group:
                    break

                progsList = ["[  TO MAIN MENU  ]"]
                progsList += self.getSubgroup(group, query)
                entry     = self.call_method("subMenu", [group, progsList])["prog"]

                self.logger.debug(entry)
                if entry not in baseOptions:
                    self.logger.info("[Executing Program] Group: {} Entry: {}".format(group, entry))
                    self.executeProgram(group, entry)
            except Exception as e:
                self.logger.error(e)


    def call_method(self, method_name, data = None):
        mName  = str(method_name)
        method = getattr(self, mName, lambda data: "No valid key passed...\nkey= " + mName + "\nargs= " + data)
        return method(data) if data else method()


    def getDesktopFilesInfo(self, paths):
        menuObjs = {
            "Accessories": [],
            "Multimedia": [],
            "Graphics": [],
            "Game": [],
            "Office": [],
            "Development": [],
            "Internet": [],
            "Settings": [],
            "System": [],
            "Wine": [],
            "Other": []
        }

        for path in paths:
            if not "/opt/" in path:
                self.listAndUpdateDesktopFiles(path, menuObjs);
            else:
                for folder in listdir(path):
                    try:
                        fPath = path + folder + "/"
                        self.listAndUpdateDesktopFiles(fPath, menuObjs);
                    except Exception as e:
                        self.logger.debug(e)

        return menuObjs

    def listAndUpdateDesktopFiles(self, path, menuObjs):
        for f in listdir(path):
            fPath = path + f
            if isfile(fPath) and f.endswith(".desktop"):
                xdgObj = DesktopEntry(fPath)

                title    = xdgObj.getName()
                groups   = xdgObj.getCategories()
                comment  = xdgObj.getComment()
                # icon     = xdgObj.getIcon()
                mainExec = xdgObj.getExec()
                tryExec  = xdgObj.getTryExec()

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

                menuObjs[group].append( {"title":  title,   "groups": groups,
                                        "comment": comment, "exec": mainExec,
                                        "tryExec": tryExec, "fileName": f
                                        })


    def getSubgroup(self, group, query = ""):
        desktopObjs = []
        if "Search..." in group:
            gkeys = self.menuData.keys()
            for gkey in gkeys:
                for opt in self.menuData[gkey]:
                    keys = opt.keys()
                    if "comment" in keys and len(opt["comment"]) > 0 :
                        if query.lower() in opt["comment"].lower():
                            desktopObjs.append( opt["title"] + " || " + opt["comment"] )
                    if query.lower() in opt["title"].lower() or query.lower() in opt["fileName"].lower():
                            desktopObjs.append( opt["title"] + " || " + opt["fileName"].replace(".desktop", "") )
        elif "Favorites" in group:
            pass
        else:
            for opt in self.menuData[group]:
                keys = opt.keys()
                if "comment" in keys and len(opt["comment"]) > 0 :
                    desktopObjs.append( opt["title"] + " || " + opt["comment"] )
                else:
                    desktopObjs.append( opt["title"] + " || " + opt["fileName"].replace(".desktop", "") )

        return desktopObjs


    def executeProgram(self, group, entry):
        parts   = entry.split("||")
        program = parts[0].strip()
        comment = parts[1].strip()

        if "Search..." in group:
            gkeys = self.menuData.keys()
            for gkey in gkeys:
                self.pre_execute(self.menuData[gkey], program, comment)
        else:
            self.pre_execute(self.menuData[group], program, comment)


    def pre_execute(self, options, program, comment):
        for opt in options:
            if program in opt["title"]:
                keys = opt.keys()
                if comment in opt["comment"] or comment in opt["fileName"]:
                    try:
                        self.execute(opt["tryExec"])
                    except Exception as e:
                        try:
                            if "exec" in keys and len(opt["exec"]):
                                self.execute(opt["exec"])
                        except Exception as e:
                            self.logger.debug(e)


    def execute(self, option):
        DEVNULL = open(os.devnull, 'w')
        command = option.split("%")[0]
        self.logger.debug(command)
        subprocess.Popen(command.split(), start_new_session=True, stdout=DEVNULL, stderr=DEVNULL)


    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')
