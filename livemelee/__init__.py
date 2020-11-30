'''An easier way to develop a SSBM bot. Built off libmelee.

.. include:: ./documentation.md'''

# don't want to clutter namespace with their many members
from . import utils
from . import inputs

from .startup import start_game
from .interact import LiveGameStats
from .bots import Bot, InputsBot, CheckBot, ControllableBot

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
    'LiveGameStats',
    'Bot', 'InputsBot', 'CheckBot', 'ControllableBot',
    'inputs',
    'utils',
]
