'''Demo of input making, bot creation, and game start.'''

from melee2 import start_game, LiveGameStats
from melee2 import Bots
from melee2.inputs import *
from melee2.patches import _Controller

# one line demo!
# start_game((Bot(), Bot(), None, None))

# longer demo:
teabag = [(down,), *wait(5), (center,), *wait(5)]
toxic_sequence = [      # create a sequence of controller inputs
    *repeat(2, *teabag),
    *taunt(),
    *wait(120)
]

class ReformBot(Bots.CheckBot):
    # builds on CheckBot funcs and attrs; check them out

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.commands = {           # call these functions midgame by keypress
            'c': (lambda: _Controller(self.controller.current), # logging func
                  'inspect controller'),                        # descrip
            'reform': self.stop,    # another func, no descrip is ok
        }
        self.set_timer(n=150,
                       do=lambda: self.perform(toxic_sequence),
                       repeat=True)
    def stop(self):
        self.do = lambda:None

bot = ReformBot()
dummy = Bots.Bot()

live_interface = LiveGameStats(commands=bot.commands)   # init live thread
                                                        # adding our new cmds
start_game((dummy, bot, None, None),   # use ports 1 and 2
           live_interface=live_interface)   # dont forget to pass custom obj
