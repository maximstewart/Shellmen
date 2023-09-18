# Python imports
import pickle
from os import listdir
from dataclasses import fields

# Lib imports
from xdg.DesktopEntry import DesktopEntry

# Application imports



class DdesktopFiles:
    def __init__(self):

        self.application_dirs = settings.config.application_dirs
        self.desktop_enteries = []
        self.groups           = {}

        self._setup_styling()
        self._setup_signals()
        self._subscribe_to_events()
        self.reload_desktop_entries()
        self.create_groups_mapping()


    def _setup_styling(self):
        ...

    def _setup_signals(self):
        ...

    def _subscribe_to_events(self):
        event_system.subscribe("reload_desktop_entries", self.reload_desktop_entries)
        event_system.subscribe("get_desktop_entries", self.get_desktop_entries)
        event_system.subscribe("get_search_results", self.get_search_results)
        event_system.subscribe("get_favorites_results", self.get_favorites_results)
        event_system.subscribe("get_sub_group", self.get_sub_group)


    def reload_desktop_entries(self):
        self.desktop_enteries.clear()
        self.desktop_enteries = None
        self.desktop_enteries = []
        self.collect_desktop_entries()

        self.groups = None
        self.groups = {}
        self.create_groups_mapping()

    def collect_desktop_entries(self):
        for path in self.application_dirs:
            for f in listdir(path):
                if f.endswith(".desktop"):
                    self.create_desktop_entry(f"{path}/{f}")

    def create_desktop_entry(self, path):
        xdg_object = DesktopEntry(path)

        if xdg_object.getHidden() or xdg_object.getNoDisplay():
            return

        type = xdg_object.getType()
        if type == "Application":
            self.desktop_enteries.append(xdg_object)

    def create_groups_mapping(self):
        self.create_default_groups()
        self.generation_primary_group_mapping()
        self.cross_append_groups()

    def create_default_groups(self):
        for slot in settings.filters.__slots__:
            self.groups[slot.title()] = []

    def generation_primary_group_mapping(self):
        for entry in self.desktop_enteries:
            groups = entry.getCategories()
            if not groups:
                self.groups["Other"].append(entry)

            for group in groups:
                if not group in self.groups.keys():
                    self.groups[group] = []

                self.groups[group].append(entry)

    def cross_append_groups(self):
        fields_data = fields(settings.filters)
        for field in fields_data:
            title    = field.name.title()
            to_merge = []

            for group in field.default_factory():
                to_merge += self.groups[group]

            sub_map = {}
            # NOTE: Will "hash" filters ("to_merge" var) first so that target self.groups[title] overrites with its own if any entry exists.
            for entry in to_merge + self.groups[title]:
                s1 = pickle.dumps(entry)
                str_version = s1.decode('unicode_escape')
                sub_map[str_version] = entry

            merged_set = []
            for key in sub_map.keys():
                merged_set.append(sub_map[key])

            self.groups[title] = merged_set

    def get_desktop_entries(self) -> []:
        return self.desktop_enteries

    def get_favorites_results(self, group):
        results = []

        for entry in self.desktop_enteries:
            _entry = f"{entry.getName()} || {entry.getComment()}"
            if _entry in settings.favorites["apps"]:
                try_exec  = entry.getTryExec()
                main_exec = entry.getExec()
                results.append( [_entry, f" {try_exec} || {main_exec}"] )

        return results


    def get_search_results(self, query):
        logger.debug(f"Search Query:  {query}")

        results = []
        for entry in self.desktop_enteries:
            title     = entry.getName()
            comment   = entry.getComment()
            if query in title.lower() or query in comment.lower():
                try_exec  = entry.getTryExec()
                main_exec = entry.getExec()
                results.append( [f"{title} || {comment}", f" {try_exec} || {main_exec}"] )

        return results

    def get_sub_group(self, group):
        results = []

        for entry in self.groups[group]:
            results.append( [f"{entry.getName()} || {entry.getComment()}", f" {entry.getTryExec()} || {entry.getExec()}"] )

        return results
