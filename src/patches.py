'''Monkey patching QOL additions to melee package, v0.20.2'''

from melee import ControllerState, Button, Menu

class _Controller(ControllerState):
    '''new controller state class with comparisons and smaller debug output.

    >>> comparable_controller = _Controller(real_controller.current)'''

    def __init__(self, existing):
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
        if not self.main_stick == (.5, .5): # perhaps rare float comparison error? not important now
            active.add(Button.BUTTON_MAIN)
        if not self.c_stick == (.5, .5):
            active.add(Button.BUTTON_C)
        if not self.l_shoulder == 0:
            active.add(Button.BUTTON_L)
        if not self.r_shoulder == 0:
            active.add(Button.BUTTON_R)
        return active

    def __str__(self):
        btns = self.active()
        return ' '.join(str(b) for b in btns) if btns else 'neutral'
        # return ' '.join('{}:{}'.format(btn,pressed) for btn,pressed in self.button.items())

    def __eq__(self, other):
        # any buttons in different state?
        # should also compare stick positions (and then L/R amount) but oh well
        if isinstance(other, _Controller):
            return len(self - other) == 0
        return False

    def __sub__(self, other):
        return self.active() - other.active()

class _Gamestat:
    '''Group of functions for helpful stats, given melee.Gamestate.
    These would be nice properties implemented in that class.
    Mostly pretty printing.

    >>> stat_output = Gamestat.func(real_gamestate_obj)'''

    def in_game(g):
        return g.menu_state == Menu.IN_GAME


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
    def actions(g):
        return 'Action states: {}  {}'.format(g.player[1].action,
                                              g.player[2].action)
    def stocks(g):
        return 'Stocks: {}  {}'.format(g.player[1].stock,
                                       g.player[2].stock)
