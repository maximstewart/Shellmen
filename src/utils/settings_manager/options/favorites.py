# Python imports
from dataclasses import dataclass, field

# Lib imports

# Application imports


@dataclass
class Favorites:
    apps: list = field(default_factory=lambda: [])
