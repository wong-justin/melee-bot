'''An easier way to develop a SSBM bot. Built off libmelee.

.. include:: ./documentation.md'''
# don't want to clutter namespace with their many members
# must come first bc other files reference capital alias
from . import stat as Stat
from . import inputs as Inputs

from .startup import start_game
from .interact import LiveInputsThread, LiveGameStats
from .bots import Bot, InputsBot, CheckBot, ControllableBot
from .patches import _Controller
from . import inputs
