'''Group of functions returning helpful stats, mainly info from gamestates.

Two kinds of gamestate functions:
    conditions returning bools, and
    pretty printers returning strings.

Also included is a controller state wrapper: `loggable_controller()`.

These would be nice additions to the libmelee package,
but we make do with this patchy submodule.

>>> stat_output = utils.func(real_gamestate_obj)

>>> print( utils.loggable_controller(controller.current) )'''

from melee import ControllerState, Button, Menu, Action

### gamestate utils

### conditions
# todo: replace hard coded ports

def in_game(g):
    return g.menu_state in (Menu.IN_GAME, Menu.SUDDEN_DEATH)

def not_taunting(gamestate):
    return not gamestate.player[2].action in (Action.TAUNT_LEFT,
                                              Action.TAUNT_RIGHT)
def grounded(gamestate):
    return gamestate.player[2].on_ground


### pretty printing


def gamestate(g):
    return 'Gamestate: {}'.format(g)

def frame_num(g):
    return 'Frame num: {}'.format(g.frame)

def menu(g):
    return 'Menu: {}'.format(g.menu_state)

def distance(g):
    return 'Distance: {:4f}'.format(g.distance)

def percents(g):
    return 'Percents: {}%  {}%'.format(g.player[1].percent,
                                     g.player[2].percent)

# def percents(g, my_port, other_port):
#     return 'Percents: {}%  {}%'.format(g.player[my_port].percent,
#                                        g.player[other_port].percent)

def actions(g):
    return 'Action states: {}  {}'.format(g.player[1].action,
                                        g.player[2].action)
def stocks(g):
    return 'Stocks: {}  {}'.format(g.player[1].stock,
                                 g.player[2].stock)

def controller1(g):
    return 'Controller: ' + str(loggable_controller(g.player[1].controller_state))

### controller wrapper

class _ComparableState(ControllerState):
    '''Extending with comparisons and smaller debug output.'''

    def __init__(self, existing):
        # constructor copying a melee.ControllerState
        self.button = {**existing.button}   # deepcopy for dict
        self.main_stick = existing.main_stick
        self.c_stick = existing.c_stick
        self.l_shoulder = existing.l_shoulder
        self.r_shoulder = existing.r_shoulder

    def active(self):
        # returns set of buttons(+sticks) not in default position
        # digitals
        active = {btn for btn, pressed in self.button.items() if pressed}
        # analogs

        active.add((Button.BUTTON_MAIN, *self.main_stick))
        active.add((Button.BUTTON_L, self.l_shoulder))
        # if not self.main_stick == (.5, .5): # perhaps rare float comparison error? not important now
        #     active.add(Button.BUTTON_MAIN)
        # if not self.c_stick == (.5, .5):
        #     active.add(Button.BUTTON_C)
        # if not self.l_shoulder == 0:
        #     active.add(Button.BUTTON_L)
        # if not self.r_shoulder == 0:
        #     active.add(Button.BUTTON_R)
        return active

    def __str__(self):
        btns = self.active()
        return ' '.join(str(b) for b in btns) if btns else 'neutral'
        # return ' '.join('{}:{}'.format(btn,pressed) for btn,pressed in self.button.items())

    def __eq__(self, other):
        # any buttons in different state?
        # should also compare stick positions (and then L/R amount) but oh well
        if isinstance(other, _ComparableState):
            return len(self - other) == 0
        return False

    def __sub__(self, other):
        return self.active() - other.active()

def loggable_controller(controller_state):
    '''Returns comparable controller state with smaller debug output.

    >>> print( loggable_controller(controller.current) )
    >>> print(( loggable_controller(controller.current) ==
    >>>         buttons(controller.prev) ))'''
    return _ComparableState(controller_state)
