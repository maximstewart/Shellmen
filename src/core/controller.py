# Python imports

# Lib imports

# Application imports
from .mixins.processor_mixin import ProcessorMixin
from .controller_data import ControllerData
from .widgets.desktop_files import DdesktopFiles
from .widgets.menu import Menu



class Controller(ProcessorMixin, ControllerData):
    def __init__(self, args, unknownargs):
        self.setup_controller_data()

        self._setup_styling()
        self._setup_signals()
        self._subscribe_to_events()
        self._load_widgets(args, unknownargs)


    def _setup_styling(self):
        ...

    def _setup_signals(self):
        ...

    def _subscribe_to_events(self):
        event_system.subscribe("execute_program", self.execute_program)
        event_system.subscribe("clear_console", self.clear_console)

    def _load_widgets(self, args, unknownargs):
        DdesktopFiles()
        Menu(args, unknownargs)
