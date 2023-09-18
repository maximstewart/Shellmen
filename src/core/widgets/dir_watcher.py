# Python imports

# Lib imports
from libs.watchdog.observers import Observer
from libs.watchdog.events import FileSystemEventHandler

# Application imports



class ShellmenFSWatcher(FileSystemEventHandler):
    """docstring for ShellmenFSWatcher."""

    def __init__(self):
        super(ShellmenFSWatcher, self).__init__()


    def on_any_event(self, event):
        if not event.event_type in ["opened", "closed"]:
            event_system.emit("reload_desktop_entries")



class DirWatcher:
    def __init__(self):

        self.application_dirs = settings.config.application_dirs

        self._setup_styling()
        self._setup_signals()
        self._subscribe_to_events()
        self._load_widgets()

    def _setup_styling(self):
        ...

    def _setup_signals(self):
        ...

    def _subscribe_to_events(self):
        ...

    def _load_widgets(self):
        for path in self.application_dirs:
            self.create_watcher(path)

    def create_watcher(self, path):
        event_handler = ShellmenFSWatcher()
        observer      = Observer()

        observer.schedule(event_handler, path, recursive = False)
        observer.start()
        # try:
        #     while True:
        #         time.sleep(1)
        # finally:
        #         observer.stop()
        #         observer.join()
