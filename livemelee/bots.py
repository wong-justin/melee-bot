'''Collection of bot classes to extend.'''

import melee
from melee import MenuHelper, Menu
import random
import time
from . import inputs as Inputs
from . import utils
import inspect

Buttons = melee.enums.Button
Actions = melee.enums.Action

DEFAULT_CHAR = melee.Character.FOX
DEFAULT_STAGE = melee.Stage.FINAL_DESTINATION

def _set_random_analogs(controller):
    # preparing for port detection
    x, y, L = ( round(random.random(), 2) for _ in range(3) )
    # stick = (True, Buttons.BUTTON_MAIN, x, y)
    # trigger = (True, Buttons.BUTTON_L, L)
    # frame1_seq = [(stick, trigger,)]
    print(x, y, L)
    controller.tilt_analog(Buttons.BUTTON_MAIN, x, y)
    controller.press_shoulder(Buttons.BUTTON_L, L)
    return x, y, L

def _get_analogs(controller_state):
    # during port detection
    x, y = controller_state.main_stick
    L = controller_state.l_shoulder
    return x, y, L

class PortBot:
    def __init__(self):
        self.controller = None
        self.character = DEFAULT_CHAR
        self.stage = DEFAULT_STAGE
        self._finished_stage = False
        self._last_gamestate = None

    def act(self, gamestate):
        self._last_gamestate = gamestate

        if utils.in_game(gamestate):
            # if gamestate.frame == -1:   #-123:  # first frame (i think)
            #     self._detect_ports(gamestate)
            if gamestate.frame == -1:   #-123:  # first frame (i think)
                self._vals = _set_random_analogs(self.controller)
            elif gamestate.frame == 0:
                self._detect_ports(gamestate)
            else:
                self.play_frame(gamestate)
        else:
            self._menu_nav(gamestate)

    def _menu_nav(self, gamestate):
        # normal menu helper except set rand inputs for frame 1 port detection after last step (selecting stage)
        # copypasted from melee.menu_helper_simple

        # If we're at the character select screen, choose our character
        if gamestate.menu_state in (Menu.CHARACTER_SELECT, Menu.SLIPPI_ONLINE_CSS):
            if gamestate.submenu == melee.SubMenu.NAME_ENTRY_SUBMENU:
                MenuHelper.name_tag_index = MenuHelper.enter_direct_code(gamestate=gamestate,
                                                                         controller=self.controller,
                                                                         # connect_code=connect_code,
                                                                         index=melee.MenuHelper.name_tag_index)
            else:
                MenuHelper.choose_character(character=self.character,
                                            gamestate=gamestate,
                                            controller=self.controller,
                                            # cpu_level=cpu_level,
                                            # costume=costume,
                                            # swag=swag,
                                            start=True)#autostart)
        # If we're at the postgame scores screen, spam START
        elif gamestate.menu_state == Menu.POSTGAME_SCORES:
            MenuHelper.skip_postgame(controller=self.controller)
        # If we're at the stage select screen, choose a stage
        elif gamestate.menu_state == Menu.STAGE_SELECT and not self._finished_stage:

            ## new insert, not in libmelee
            # listen for A press on controller, signaling about to start game
            if self.controller.current.button[Buttons.BUTTON_A]:
                # self._vals = _set_random_analogs(self.controller)
                self._finished_stage = True
            else:

                # normal from libmelee
                MenuHelper.choose_stage(stage=self.stage,
                                        gamestate=gamestate,
                                        controller=self.controller)
        elif gamestate.menu_state == Menu.MAIN_MENU:
            # if connect_code:
            #     MenuHelper.choose_direct_online(gamestate=gamestate, controller=self.controller)
            # else:
            #     MenuHelper.choose_versus_mode(gamestate=gamestate, controller=self.controller)
            MenuHelper.choose_versus_mode(gamestate=gamestate, controller=self.controller)

    def _detect_ports(self, gamestate):
        # returns port num for this bot and opponent, eg. (1,2).
        # needs to be in game
        # - set stick, L/R to random values
        # - first frame of game, check gamestate controller states to find matching vals
        # unlikely that the other player has the same analog vals.
        # set controller after choosing stage? that way frame 1 of game is checking and releasing,
        # as opposed to frame 1 setting and frame 2 checking + releasing, leaving f3 actionable.
        # will this buffer any inputs?
        # what's the float precision in controller state?
        mine = -1
        other = -1
        print('detecting..')
        # self._vals = _set_random_analogs(controller)
        for port, pstate in gamestate.player.items():
            these_vals = _get_analogs(pstate.controller_state)
            print(these_vals) #
            if self._vals == these_vals:
                mine = port
            else:
                other = port

        self.ports = (mine, other)
        return mine, other

    def get_controller_state(self):
        return 'From controller: {}\nFrom gamestate: {}'.format(
            utils.loggable_controller(self.controller.current),
            utils.get_controller(self._last_gamestate, 1) )

    def play_frame(self, gamestate):
        pass



class Bot:
    '''Framework for making controller inputs.
    Offline only implementation currently.

    Attributes:
        controller: melee.Controller
        character: melee.Character
        stage: melee.Stage'''

    def __init__(self, controller=None,
                 character=DEFAULT_CHAR,
                 stage=DEFAULT_STAGE):
        self.controller = controller
        self.character = character
        self.stage = stage

    def act(self, gamestate):
        '''Main function called each frame of game loop with updated gamestate.'''

        # if gamestate.menu_state in (melee.Menu.IN_GAME,
        #                             melee.Menu.SUDDEN_DEATH):
        if utils.in_game(gamestate):
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

def always(gamestate):
    return True

def never(gamestate):
    return False

class InputsBot(Bot):
    '''Adds inputs queue to Bot.

    Inputs should be always put into queue,
    never called directly/instantly with controller.
    First queued input will happen same frame of queueing.

    Attributes:
        queue: list of inputs as outlined in inputs.py'''

    def __init__(self, controller=None,
                 character=DEFAULT_CHAR,
                 stage=DEFAULT_STAGE):
        super().__init__(controller, character, stage)
        self.queue = []

    def play_frame(self, gamestate):
        self.check_frame(gamestate)
        self.consume_next_inputs()

    def consume_next_inputs(self):
        '''Called each frame to press or release next buttons in queue.
        See inputs.py for expected inputs format.'''
        if self.queue:
            inputs = self.queue.pop(0)
            Inputs.make_inputs(inputs, self.controller)

    def perform(self, input_sequence):
        '''Set queue to a sequence of inputs.
        Useful in lambdas where assignment is not allowed.'''
        self.queue = list(input_sequence)  # need a (deep) copy for modifiable lists/tuples

    def check_frame(self, gamestate):
        '''Override this (instead of overriding play_frame).
        Decision making and input queueing happen here.'''
        pass

class CheckBot(InputsBot):
    '''Adds condition checker to main loop.

    Attributes:
        when: (ie trigger) condition called every frame (func taking gamestate)

        do: (ie on_trigger) func called when condition returns True

    By default, stops checking upon reaching condition.
    `set_timer()` is an example of using `when` and `do`.

    Eg.
    `self.repeat(when=self.finished_inputs, do=some_func)`'''

    def __init__(self, controller=None,
                 character=DEFAULT_CHAR,
                 stage=DEFAULT_STAGE):
        super().__init__(controller, character, stage)

        self.when = never
        self.do = lambda:None
        self._max_time = 30  # arbitrary init
        self._timer = self._max_time

    def check_frame(self, gamestate):
        '''Called each frame to check gamestate (and/or possibly self?) for condition,
        stopping check when True.'''
        if self.when(gamestate):
            self.when = never
            self.do()

    def set_timer(self, n, do, repeat=True):
        '''Set all required timer functions:
        n frames to wait, timer condition, callback.'''
        self._max_time = n
        self._timer = self._max_time
        if repeat:
            self.repeat(when=self._times_up,
                        do=do)
        else:
            self.when = self._times_up
            self.do = do

    def _times_up(self, gamestate):
        '''A condition check that ticks timer, returning True on expire.'''
        if self._timer > 0:
            self._timer -= 1
            return False
        else:
            self._timer = self._max_time
            return True

    def repeat(self, when, do):
        '''Keeps checking when condition (as opposed to the default stop checking).'''
        def do_and_wait_again():
            do()
            self.when = when
        self.when = when
        self.do = do_and_wait_again

    def finished_inputs(self, gamestate):
        '''A condition to loop inputs by returning True when queue is empty.

        Eg.
        ```
        self.when = self.finished_inputs
        self.do = something
        ```'''
        return len(self.queue) == 0

class ControllableBot(InputsBot):
    '''Designed to easily control externally in real time,
    eg. from live thread or perhaps something like a chat.

    Attributes:
        commands: dict of `{'cmd': (func, 'description')}`
            See LiveInputsThread for details.'''

    def __init__(self, controller=None,
                 character=melee.Character.FALCO,
                 stage=DEFAULT_STAGE):
        super().__init__(controller, character, stage)

        self.commands = self._init_commands()
        self._curr_sequence = []

    def _init_commands(self):

        commands = {cmd: self._set_seq(make_seq) for cmd, make_seq in {
            'laser': Inputs.laser,
            'sh': Inputs.shorthop,
            'shlaser': Inputs.jump_n_laser,  #fastfall_laser_rand
            'taunt': Inputs.taunt,
            'shield': Inputs.shield,
            'dd': Inputs.dashdance,
        }.items()}
        commands.update({cmd: self._set_seq(_make_seq(btn)) for cmd, btn in {
            'release': Inputs.release,
            'center': Inputs.center,
            'down': Inputs.down,
            'up': Inputs.up,
            'left': Inputs.left,
            'right': Inputs.right,
            'A': Inputs.A,
            'B': Inputs.B,
            'Y': Inputs.Y,
            'L': Inputs.L
        }.items()})
        # commands.update({
        #     'undo': self.release_last,
        # })
        return commands

    def _set_seq(self, make_seq):
        # wrapper to set current sequence to result of sequence maker func
        return lambda: self.set_curr_seq(make_seq())

    def set_curr_seq(self, inputs):
        self._curr_sequence = inputs# [(Inputs.release,), *inputs]

    def add_to_queue(self, inputs):
        # add to any existing inputs (usually would replace them)
        self.queue.extend(inputs)

    def check_frame(self, gamestate):
        # keep doing current sequence, looping if finished

        if len(self.queue) == 0:
            self.perform(self._curr_sequence)
        # if self.timer == 0:
        #     self.queue = Inputs.laser

def _make_seq(button):
    # wrapper to put single button press into a sequence
    return lambda: [(button,),]

class FalcoBot(CheckBot):
    # working with previous features

    def __init__(self):
        super().__init__(character=melee.Character.FALCO)

        # self.investigate_jumpframes()
        self.jumped = False
        self.set_shorthop_laser_strat()

    def set_standing_laser_strat(self):
        self.set_timer(2, lambda: self.perform(Inputs.laser()), repeat=True)
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
        if utils.grounded(gamestate):
            if self.jumped:
                return False
            else:
                return True
        else:
            self.jumped = False # safe to reset now
            return False

    def sh_laser(self):
        self.perform([*Inputs.wait(3), *Inputs.fastfall_laser_rand()])
        self.jumped = True

    def jump(self):
        self.perform([*Inputs.wait(3), *Inputs.shorthop()])
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
                if not utils.grounded(gamestate):
                    self.jumped = True  # should be success but just let timer tick
            return False

        self.repeat(when=timer_checking_jump,
                    do=self.jump_with_wait)

    def jump_with_wait(self):
        self.perform([*Inputs.wait(self.prepause), *Inputs.shorthop()])

    ### toxic demos, use responsibly

    def taunt(self):
        # interrupt activities to taunt asap.
        # keeps setting queue until taunting actually happens

        # self.last_when = self.when
        self.when = utils.not_taunting
        self.do = lambda: self.perform([(Inputs.release,), *Inputs.taunt()])

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

# under construction:

def _with_ports(self, func):
    def stat_with_ports(gamestate):
        return func(gamestate, self.my_port, self.opp_port)
    return stat_with_ports

def detect_ports(self, gamestate):
    # melee.GameState.port_detector(gamestate, self.character, self.costume)
    players = gamestate.player.items()

    #
