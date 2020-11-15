'''Botless use of LiveInputsThread acting as a hook to trigger
when something happens in game.'''

import argparse
from interact import LiveInputsThread
from melee import Console
from patches import _Gamestat

parser = argparse.ArgumentParser()
parser.add_argument('path', help='dolphin directory')
console = Console(path=parser.parse_args().path)
console.run()
console.connect()

class GameHook(LiveInputsThread):

    def __init__(self, *args, **kwargs):
        self.last_percent = -1
        super().__init__(*args, **kwargs)

    def update(self, gamestate):

        if _Gamestat.in_game(gamestate):

            percent, has_changed = self.new_percent(gamestate)
            if has_changed:
                if percent == 69:
                    print('power up')
                    # stream.celebrate()
                self.last_percent = percent

    def new_percent(self, gamestate):
        percent = gamestate.player[2].percent
        changed = not percent == self.last_percent
        return percent, changed

hook = GameHook(onshutdown=console.stop)
while True:
    gamestate = console.step()
    if not gamestate:
        break
    hook.update(gamestate)
