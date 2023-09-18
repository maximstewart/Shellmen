# Python imports

# Lib imports

# Application imports
from core.controller import Controller



class ControllerStartExceptiom(Exception):
    ...



class ApplicationWindow:
    """docstring for ApplicationWindow."""

    def __init__(self):
        ...

class Window(ApplicationWindow):
    """ docstring for Window. """

    def __init__(self, args, unknownargs):
        super(Window, self).__init__()
        settings_manager.set_main_window(self)

        self._controller = None

        self._setup_styling()
        self._setup_signals()
        self._subscribe_to_events()
        self._load_widgets(args, unknownargs)


    def _setup_styling(self):
        ...

    def _setup_signals(self):
        ...

    def _subscribe_to_events(self):
        event_system.subscribe("tear_down", self._tear_down)

    def _load_widgets(self, args, unknownargs):
        self._controller = Controller(args, unknownargs)
        if not self._controller:
            raise ControllerStartException("Controller exited and doesn't exist...")

    def _tear_down(self, widget = None, eve = None):
        settings_manager.save_settings()
