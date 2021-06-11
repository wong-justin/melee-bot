'''Put an object tracking gamestates in a port instead of a bot.
Then you can do things like trigger a callback according to a game condition.
Kind of like writing a live py slippi parser.'''

from livemelee import start_game, Bot, InputsBot, utils, inputs
from melee import Stage, Character

class GameHook:

    def __init__(self):
        self.last_gamestate = None   # store most recent frame data

    def act(self, gamestate):        # main method, checks each frame

        if utils.in_game(gamestate):

            percent = self.parse_p2_percent(gamestate)
            if not percent == self.parse_p2_percent(self.last_gamestate):
                if percent == 69:
                    print('P2 at gamer percent')
                    # stream.celebrate() or some other useful callback

        self.last_gamestate = gamestate

    def parse_p2_percent(self, gamestate):   #  condition compares current to last frame
        return gamestate.player[2].percent

hook = GameHook()

# testing with bots:

# class LaserBot(InputsBot):
#
#     def check_frame(self, gamestate):
#         if gamestate.frame % 2 == 0:
#             self.perform([
#                 (inputs.B,),
#                 (inputs.un_B,),
#             ])
##
# laser_bot = LaserBot(stage=Stage.FINAL_DESTINATION, character=Character.FOX)
# dummy = Bot(stage=Stage.FINAL_DESTINATION)

# start_game((laser_bot, dummy, None, hook), {


# testing without bots: human in port 1, go to CSS and make normal CPU port 2
# test commands during gameplay to show current stats

start_game((None, None, None, hook), {
    # these utils functions return a formatted string with stats for P1 and P2, given a game state
    'f': (lambda: utils.frame_num(hook.last_gamestate), 'frame num'),
    'p': (lambda: utils.percents(hook.last_gamestate), 'percents'),
    'd': (lambda: utils.distance(hook.last_gamestate), 'distance'),
    'a': (lambda: utils.actions(hook.last_gamestate), 'action states'),
    's': (lambda: utils.stocks(hook.last_gamestate), 'stocks'),
})
