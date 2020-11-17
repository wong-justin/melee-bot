'''Using LiveInputsThread as a hook to trigger when something happens in game.
Kind of like writing your own py slippi parser.'''

from livemelee import start_game, LiveInputsThread, Stat

class GameHook(LiveInputsThread):

    def __init__(self, *args, **kwargs):
        self.last_percent = -1          # init a stat of interest
        super().__init__(*args, **kwargs)

    def update(self, gamestate):        # main method, checks each frame

        if Stat.in_game(gamestate):

            percent, has_changed = self.new_percent(gamestate)
            if has_changed:
                if percent == 69:
                    print('power up')
                    # stream.celebrate() or something external like that
                self.last_percent = percent

    def new_percent(self, gamestate):   #  compares current to last frame
        percent = gamestate.player[2].percent
        changed = not percent == self.last_percent
        return percent, changed

hook = GameHook()

start_game((None, None, None, None), live_interface=hook) # ports open for human
