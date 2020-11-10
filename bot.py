import melee
import random
import time

Buttons = melee.enums.Button
Actions = melee.enums.Action

class Bot:
    '''Framework for making controller inputs.
    Offline only implementation currently.'''

    def __init__(self, controller,
                 character=melee.Character.FOX,
                 stage=melee.Stage.FINAL_DESTINATION):
        self.controller = controller
        self.character = character
        self.stage = stage

    def act(self, gamestate):
        '''Main function called each frame of game loop with updated gamestate.'''

        if gamestate.menu_state in (melee.Menu.IN_GAME,
                                    melee.Menu.SUDDEN_DEATH):
            self.play_frame(gamestate)  # rand note, paused wont advance frame
        else:
            self.menu_nav(gamestate)

    def menu_nav(self, gamestate):
        '''Processes menus with given character, stage.'''
        melee.MenuHelper.menu_helper_simple(gamestate,
                                            self.controller,
                                            self.character,
                                            self.stage,
                                            '', # connect code
                                            0,  # cpu_level (0 for N/A)
                                            0,  # costume
                                            autostart=True)

    def play_frame(self, gamestate):
        '''Bot game logic implemented here.'''
        pass

# convenience/helpers/conditions that don't require self

def always(gamestate):
    return True

def never(gamestate):
    return False

class CheckingBot(Bot):
    '''Adds inputs queue and condition checker to main loop.

    Inputs should be always put into queue,
    never called directly/instantly with controller.
    First input will happen same frame of queueing.

    Condition functions (self.when) take a gamestate parameter.
    Callbacks (self.do) take no parameters.
    Set self.when again in self.do in order to loop strategy,
    otherwise self.when stops checking.'''

    def __init__(self, controller,
                 character=melee.Character.FOX,
                 stage=melee.Stage.FINAL_DESTINATION):
        super().__init__(controller=controller,
                         character=character,
                         stage=stage)

        self.when = never
        self.do = lambda:None
        self.queue = []     # perhaps use a smarter/slightly more efficent type (like a real queue)?
        self.max_time = 30  # arbitrary init
        self.timer = self.max_time

    def play_frame(self, gamestate):

        # a fix for leftover menu presses
        if gamestate.frame < 0:
            self.queue = [(release_all,)]
            return

        self.check(gamestate)
        self.consume_next_inputs()

    def check(self, gamestate):
        '''Called each frame to check gamestate (and/or possibly self?) for condition,
        stopping check when True.'''
        if self.when(gamestate):
            self.when = never
            self.do()

    def consume_next_inputs(self):
        '''Called each frame to press or release queued buttons.
        (True, btn, x, y)   tilt_analog
        (True, btn)         press_btn
        (False, btn)        release_btn
        (False,)            release_all
        []                  no inputs this frame
        Queue example:
        >>> self.queue = [
            ((True, Buttons.BUTTON_MAIN, 0.5, 0), (True, Buttons.BUTTON_B)),    # down+b same frame
            [],                             # wait a frame
            ((True, Buttons.BUTTON_Y),),    # jump input
            ((False,),)                     # everything back to default
        ]'''
        if self.queue:
            commands = self.queue.pop(0)
            for press, *button_args in commands:
                if len(button_args) > 1:
                    self.controller.tilt_analog(*button_args)
                else:
                    if press:
                        self.controller.press_button(*button_args)
                    else:
                        if button_args:
                            self.controller.release_button(*button_args)
                        else:
                            self.controller.release_all()

    def times_up(self, gamestate):
        '''A condition check that ticks timer, returning True on expire.'''
        if self.timer > 0:
            self.timer -= 1
            return False
        else:
            self.timer = self.max_time
            return True

    def set_timer(self, n, do, repeat=True):
        '''Convenience function sets all required timer functions:
        n frames to wait, timer condition, callback.'''
        self.max_time = n
        self.timer = self.max_time
        if repeat:
            self.repeat(when=self.times_up,
                        do=do)
        else:
            self.when = self.times_up
            self.do = do

    def repeat(self, when, do):
        '''Keeps checking when condition (as opposed to the default stop checking).'''
        def do_and_wait_again():
            do()
            self.when = when
        self.when = when
        self.do = do_and_wait_again

    def finished_inputs(self, gamestate):
        '''A condition to loop inputs by returning True when queue is empty.'''
        return len(self.queue) == 0

    def perform(self, inputs):
        '''Set queue to a sequence of inputs.
        Useful in lambdas where assignment is not allowed'''
        self.queue = list(inputs)  # need a (deep) copy for module level objs

# some gamestate conditions not needing self

def not_lasering(gamestate):
    # just for standing, no aerial actions
    return not gamestate.player[2].action in (Actions.LASER_GUN_PULL,
                                              Actions.NEUTRAL_B_CHARGING,
                                              Actions.NEUTRAL_B_ATTACKING)
def not_taunting(gamestate):
    return not gamestate.player[2].action in (Actions.TAUNT_LEFT,
                                              Actions.TAUNT_RIGHT)
def grounded(gamestate):
    return gamestate.player[2].on_ground

class FalcoBot(CheckingBot):
    # working with previous features

    def __init__(self, controller):
        super().__init__(controller=controller,
                         character=melee.Character.FALCO,
                         stage=melee.Stage.FINAL_DESTINATION)

        # self.investigate_jumpframes()
        self.jumped = False
        self.set_shorthop_laser_strat()

    def set_standing_laser_strat(self):
        self.set_timer(2, lambda: self.perform(laser), repeat=True)
        # self.repeat(when=self.finished_inputs,
        #             do=lambda: self.perform(laser))

    def set_shorthop_laser_strat(self):
        self.jumped = False
        self.repeat(when=self.can_jump,
                    do=self.sh_laser)

    def set_jump_strat(self):
        self.jumped = False
        self.repeat(when=self.can_jump,
                    do=self.jump)

    def can_jump(self, gamestate):
        if grounded(gamestate):
            if self.jumped:
                return False
            else:
                return True
        else:
            self.jumped = False # safe to reset now
            return False

    def sh_laser(self):
        self.perform([*wait(3), *fastfall_laser_rand()])
        self.jumped = True

    def jump(self):
        self.perform([*wait(3), *shorthop])
        self.jumped = True

    ### example of finding out frame data

    def investigate_jumpframes(self):
        self.prepause = 0
        self.jumped = False
        self.max_time = 45

        def timer_checking_jump(gamestate):
            if self.timer < 0:
                # print('timer up')
                title = 'prepause {} f,'.format(self.prepause)
                if self.jumped:
                    print(title, 'success')
                    # self.when = never
                    # return True
                else:
                    print(title, 'fail')
                # reset everything and inc pause frames
                self.timer = self.max_time
                self.prepause += 1
                self.jumped = False
                return True
            else:
                self.timer -= 1
                if not grounded(gamestate):
                    self.jumped = True  # should be success but just let timer tick
            return False

        self.repeat(when=timer_checking_jump,
                    do=self.jump_with_wait)

    def jump_with_wait(self):
        self.perform([*wait(self.prepause), *shorthop])

    ### toxic demos, use responsibly

    def taunt_asap(self):
        # interrupt activities to taunt asap.
        # keeps setting queue until taunting actually happens

        # self.last_when = self.when
        self.when = not_taunting
        self.do = self.prep_taunt

    def prep_taunt(self):
        # self.max_time = 15  # taunting should be underway by then
        # self.when = self.times_up
        # self.do = lambda:self.set_strat(self.last_strategy)
        self.perform(taunt)

    def ragequit(self): #, angry_misinput=True):
        # special pause case: frames not advanced in pause, so we have to
        # independently execute multiple presses outside of main loop.
        # generally poor use of inputs and lack of queue.
        inputs = [
            (True, Buttons.BUTTON_START),
            (True, Buttons.BUTTON_L),
            (True, Buttons.BUTTON_R),
            (True, Buttons.BUTTON_A),
        ]
        self.controller.release_all()
        for press, *button_args in inputs:
            self.controller.press_button(*button_args)
            time.sleep(0.01) # could be needed if incosistent timing?

class MoreAdvancedBot(AdvancedBot):
    # more than one check at a time

    def __init__(self, controller, character, stage):
        super().__init__(controller, character, stage)
        self.checks = {}
        self.timers = {}

    def check(self):
        for when, do in self.checks.items():
            if when(self, gamestate):
                del self.checks[when]
                do()

    def repeat(self, when, do):
        def do_and_wait_again():
            do()
            self.checks[when] = do_and_wait_again
        self.checks[when] = do_and_wait_again

### INPUTS

# convenience

def wait(n):
    '''Gives n frames of no inputs. Use * to unpack in sequence.
    >>> inputs = [
        ...,
        *wait(42),
        ...
    ]'''
    return [[]] * n
    # return [[] for _ in range(n)]

def repeat(n, *input_frames):
    return [*input_frames] * n

release_all = (False,)
center = (True, Buttons.BUTTON_MAIN, 0.5, 0.5)
down = (True, Buttons.BUTTON_MAIN, 0.5, 0)

A = (True, Buttons.BUTTON_A)
un_A = (False, Buttons.BUTTON_A)
B = (True, Buttons.BUTTON_B)
un_B = (False, Buttons.BUTTON_B)
Y = (True, Buttons.BUTTON_Y)
un_Y = (False, Buttons.BUTTON_Y)

# sequences
    # which would be faster,
    #   make these all functions-
    #       def f(): return [...inputs...]
    #   or copy in class-
    #       class ... def f(): self.queue = somedeepcopy(sequence_ref) ?
    # i think first option

laser = [
    ((True, Buttons.BUTTON_B),),
    ((False, Buttons.BUTTON_B),)
]

shorthop = [
    ((True, Buttons.BUTTON_Y),),
    # *wait(2),
    ((False, Buttons.BUTTON_Y),),
]

fastfall = [
    (down,),
    (center,),
]

jump_n_laser = [
    ((True, Buttons.BUTTON_Y),),
    ((False, Buttons.BUTTON_Y),),
    *wait(5),
    ((True, Buttons.BUTTON_B),),
    ((False, Buttons.BUTTON_B),),
]

fastfall_laser = [
    ((True, Buttons.BUTTON_Y),),
    ((False, Buttons.BUTTON_Y),),
    *wait(3),
    ((True, Buttons.BUTTON_B),),
    ((False, Buttons.BUTTON_B), (True, Buttons.BUTTON_MAIN, 0.5, 0),),
    *wait(5),
    (center,),
]

# crude
def fastfall_laser_rand():
    pre = random.randint(2,4)#10)
    post = random.randint(1,5)
    return [
        *shorthop,
        *repeat(pre, *fastfall),
        (B,),
        (un_B,),

        *repeat(post, *fastfall),      # fastfall enough til ground; queue should be reset anyways
        *wait(5),
    ]

taunt = [
    ((True, Buttons.BUTTON_D_UP),),
    ((False, Buttons.BUTTON_D_UP),)
]
