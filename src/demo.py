from setup import start_game
from bot import Bot, CheckBot
from inputs import *
from interact import LiveInputsThread, LiveGameStats
from patches import _Controller

# one line demo:
# start_game((Bot(), Bot(), None, None))

# longer demo:
teabag = [(down,), *wait(5), (center,), *wait(5)]
toxic_sequence = [
    *repeat(2, *teabag),
    *taunt(),
    *wait(120)
]

class MyBot(CheckBot):
    # uses CheckBot funcs and attrs; check them out

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.commands = {
            'c': (lambda: _Controller(self.controller.current), 'controller')
        }
        self.set_timer(n=150,
                       do=lambda: self.perform(toxic_sequence),
                       repeat=True)

my_bot = MyBot()
dummy = Bot()

live_interface = LiveGameStats(commands=my_bot.commands)

start_game((dummy, my_bot, None, None),
           live_interface=live_interface,
           log=False)
