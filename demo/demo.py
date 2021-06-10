'''Demo of input making, bot creation, and game start.'''

from livemelee import start_game, Bot, CheckBot, LiveGameStats, utils
from livemelee.inputs import *  # alternative to `from livemelee import Inputs`
                                #  and then using Inputs.down, etc
# one line demo!
# start_game((Bot(), Bot(), None, None))    # two dummy bots will sit in game

# longer demo:

# create a sequence of controller inputs
teabag = [
    (down,),    # single button input
    *wait(5),   # unpack list of 5 empty inputs
    (center,),
    *wait(5)
]
# compose into a longer sequence
toxic_sequence = [          # create another sequence of controller inputs
    *repeat(2, *teabag),
    *taunt(),
    *wait(120)
]

class ReformBot(CheckBot):
    # builds on CheckBot funcs and attrs; check them out

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.start()

    def stop(self):                 # replace toxic action with inaction
        self.do = lambda:None

    def start(self):
        self.set_timer(n=150,
                       do=lambda: self.perform(toxic_sequence),
                       repeat=True)

dummy = Bot()
bot = ReformBot()

commands = {
    # command: function, description
    'reform': (bot.stop, 'do nothing'),
    'betoxic': (bot.start, 'taunt and teabag'),
}

# run dolphin with bots in ports 2 and 3
start_game((None, dummy, bot, None), commands)
