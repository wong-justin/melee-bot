from melee import ControllerState, Button

class ComparableControllerState(ControllerState):
    '''Extending melee.ControllerState with comparisons and smaller debug output.

    These would be nice additions to melee.ControllerState,
    but we make do with this patchy class.'''

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
        if isinstance(other, ComparableControllerState):
            return len(self - other) == 0
        return False

    def __sub__(self, other):
        return self.active() - other.active()


def buttons(controller_state):
    '''Returns comparable controller state with smaller debug output.

    >>> print( buttons(controller.current) )
    >>> print( buttons(controller.current) == buttons(controller.prev) )'''
    return ComparableControllerState(controller_state)
