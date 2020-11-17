'''An easier way to develop a SSBM bot. Built off libmelee.

.. include:: ./documentation.md'''
from .startup import start_game
from .interact import LiveInputsThread, LiveGameStats
from .bots import Bot, InputsBot, CheckBot, ControllableBot
from .patches import _Gamestat, _Controller
from . import inputs    # don't want to clutter namespace
