# Features module
# Import new modules only if available to avoid errors
try:
    from . import spotify_control
except (ImportError, ModuleNotFoundError):
    spotify_control = None

try:
    from . import smart_home
except (ImportError, ModuleNotFoundError):
    smart_home = None

try:
    from . import scenarios
except (ImportError, ModuleNotFoundError):
    scenarios = None

