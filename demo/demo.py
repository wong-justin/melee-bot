'''Demo of input making, bot creation, and game start.'''

from livemelee import start_game, Bot, CheckBot, LiveGameStats, utils
from livemelee.inputs import *  # alternative to `from livemelee import Inputs`
                                #  and then using Inputs.down, etc
# one line demo!
# start_game((Bot(), Bot(), None, None))    # two dummy bots will sit in game

# longer demo:
teabag = [(down,), *wait(5), (center,), *wait(5)]   # down, center are buttons
toxic_sequence = [          # create another sequence of controller inputs
    *repeat(2, *teabag),    # unpack sequences in other sequences
    *taunt(),
    *wait(120)
]

class ReformBot(CheckBot):
    # builds on CheckBot funcs and attrs; check them out

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.commands = {          # user calls these midgame in shell by keypress
            'c': (lambda: utils.loggable_controller(self.controller.current), # logging func
                  'inspect controller'),                    # descrip
            'reform': self.stop,   # another cmd: func - no descrip is ok
        }
        self.set_timer(n=150,
                       do=lambda: self.perform(toxic_sequence),
                       repeat=True)
    def stop(self):                 # replace toxic action with inaction
        self.do = lambda:None

dummy = Bot()
bot = ReformBot()

live_interface = LiveGameStats(commands=bot.commands)   # init live thread
                                                        #  adding our new cmds
start_game((dummy, bot, None, None),        # use ports 1 and 2
           live_interface=live_interface)   # dont forget to pass that obj
