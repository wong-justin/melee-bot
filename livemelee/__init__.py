'''An easier way to develop a SSBM bot. Built off libmelee.

.. include:: ./documentation.md'''

# don't want to clutter namespace with their many members
from . import utils
from . import inputs

from .startup import start_game
# from .interact import LiveGameStats
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
    # 'LiveGameStats',
    'Bot', 'InputsBot', 'CheckBot', 'ControllableBot',
    'inputs',
    'utils',
]

__pdoc__ = {
    'interact': False,
    'startup': False,
    'livemelee.inputs.release': True,
    'livemelee.inputs.center': True,
    'livemelee.inputs.down': True,
    'livemelee.inputs.up': True,
    'livemelee.inputs.left': True,
    'livemelee.inputs.right': True,
    'livemelee.inputs.A': True,
    'livemelee.inputs.B': True,
    'livemelee.inputs.X': True,
    'livemelee.inputs.Y': True,
    'livemelee.inputs.L': True,
    'livemelee.inputs.R': True,
}
