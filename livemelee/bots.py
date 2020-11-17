import melee
import random
import time
from . import inputs as Inputs
from .patches import _Gamestat

Buttons = melee.enums.Button
Actions = melee.enums.Action

class Bot:
    '''Framework for making controller inputs.
    Offline only implementation currently.

    Attributes:
        controller: melee.Controller
        character: melee.Character
        stage: melee.Stage'''

    def __init__(self, controller=None,
                 character=melee.Character.FOX,
                 stage=melee.Stage.FINAL_DESTINATION):
        self.controller = controller
        self.character = character
        self.stage = stage

    def act(self, gamestate):
        '''Main function called each frame of game loop with updated gamestate.'''

        # if gamestate.menu_state in (melee.Menu.IN_GAME,
        #                             melee.Menu.SUDDEN_DEATH):
        if _Gamestat.in_game(gamestate):
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

    def __init__(self, controller, character, stage):
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
                 character=melee.Character.FOX,
                 stage=melee.Stage.FINAL_DESTINATION):
        super().__init__(controller=controller,
                         character=character,
                         stage=stage)

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
                 stage=melee.Stage.FINAL_DESTINATION):
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

class FalcoBot(CheckBot):
    # working with previous features

    def __init__(self, controller=None):
        super().__init__(controller=controller,
                         character=melee.Character.FALCO,
                         stage=melee.Stage.FINAL_DESTINATION)

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
        if grounded(gamestate):
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
                if not grounded(gamestate):
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
        self.when = not_taunting
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

# class MultiCheckBot(InputsBot):
#
#     FINISH_NOW = 1
#     STOP_CHECKING = 2
#     KEEP_CHECKING = 3
#
#     def __init__(self, controller,
#                  character=melee.Character.FALCO,
#                  stage=melee.Stage.FINAL_DESTINATION):
#         super().__init__(controller, character, stage)
#
#         self.checks = {}
#
#     def check_frame(self, gamestate):
#         remove = []
#         for condition, do in self.checks.items():
#             if condition(self, gamestate):
#                 retval = do()
#                 if retval == MultiCheckBot.FINISH_NOW:
#                     return
#                 elif retval == MultiCheckBot.STOP_CHECKING:
#                     remove.append(condition)
#         for condition in remove:
#             del self.checks[condition]
#
#     def something(self):
#         pass
