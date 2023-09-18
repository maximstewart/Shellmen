# Python imports
from dataclasses import dataclass, field

# Lib imports

# Application imports


@dataclass(slots = True)
class Filters:
    accessories: list = field(default_factory=lambda: [
        "Utility"
    ])
    multimedia: list = field(default_factory=lambda: [
        "Video",
        "Audio"
    ])
    graphics: list = field(default_factory=lambda: [
    ])
    game: list = field(default_factory=lambda: [
    ])
    office: list = field(default_factory=lambda: [
    ])
    development: list = field(default_factory=lambda:[
    ])
    internet: list = field(default_factory=lambda: [
        "Network"
    ])
    settings: list = field(default_factory=lambda: [
    ])
    system: list = field(default_factory=lambda: [
    ])
    wine: list = field(default_factory=lambda: [
    ])
    other: list = field(default_factory=lambda: [
    ])
