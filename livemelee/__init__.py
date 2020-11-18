'''An easier way to develop a SSBM bot. Built off libmelee.

.. include:: ./documentation.md'''

# don't want to clutter namespace with their many members
# must come first bc other files reference the capital alias
from . import stat #as Stat
from . import inputs #as Inputs

from .startup import start_game
from .interact import LiveInputsThread, LiveGameStats
from .bots import Bot, InputsBot, CheckBot, ControllableBot
from .patches import buttons

# __pdoc__ = {obj: True for obj in (
#     'start_game',
#     'LiveInputsThread', 'LiveGameStats',
#     'Bot', 'InputsBot', 'CheckBot', 'ControllableBot',
#     'buttons',
#     'Stat',
#     'Inputs'
# )}

__all__ = [
    'start_game',
    'LiveInputsThread', 'LiveGameStats',
    'Bot', 'InputsBot', 'CheckBot', 'ControllableBot',
    'buttons',
    'stat',
    'inputs'
]
