import threading
from melee import GameState

class LiveInputsThread(threading.Thread):
    '''Awaits user input to invoke functions live, eg to get live information
    or dynamically change gameplay.
    Used for debugging or poking around.
    No data saved to file (as opposed to melee.logger).
    Call self.help() for available commands.

    Ex:
    >>> live_thread.add_command('connect', bot.connect_to)
    >>> ...init + start game, this thread waiting...
    >>> connect PLUP#123'''

    def __init__(self, onshutdown, commands={}):
        self.onshutdown = onshutdown    # callback
        self.commands = {}
        for command, func in commands.items():
            self.add_command(command, func)
        self.commands['help'] = self.help
        self.stops = ('q', 'quit', 'kill', 'stop')

        super().__init__(name='input-thread')
        # self.start()

    def run(self):
        '''Start this thread waiting for user inputs, exiting if asked.'''
        self.help()
        while True:
            _input = input()
            if _input in self.stops:
                break
            self._on_input(_input)
        self.onshutdown()

    def _on_input(self, _input):
        '''Calls associated function, passing any options as args.'''
        command, options = LiveInputsThread._parse_input(_input)
        if command in self.commands:
            self.commands[command](*options)
        else:
            print('"{}" not recognized'.format(_input))

    def _parse_input(_input):
        '''Parses command-line-style args.'''
        command, *options = _input.split(' ')
        return command, [(o[1:] if o[0] == '-' else o)
                         for o in options]    # remove "-"s

    def _print_wrapper(func):
        '''Resulting function will print and return result of func().'''
        def f(*args):
            result = func(*args)
            if result:  # falsy values too ugly/unimportant, not worth a print
                print(result)
            return result
        return f

    def add_command(self, command, func):
        '''Add custom command with function.
        Func(*options) will be called when command entered.'''
        self.commands[command] = LiveInputsThread._print_wrapper(func)

    def help(self):
        '''Display available commands.'''
        print( 'Commands: {}'.format((*self.commands.keys(), *self.stops)) )

class LiveGameStats(LiveInputsThread):
    '''Enhances LiveInputsThread by adding updating/tracking feature
    and incorporating stats from melee.GameState.'''

    def __init__(self, onshutdown, console=None):
        self.max_processing = -1    # a persistent/cumulative stat
        self.console = console      # for above
        self.last_gamestate = None  # will provide rest of the stats

        self.tracker = None         # a function to check for updates
        self.tracked_last = None    # last tracker() value

        commands = {k: self._continuous_wrapper(v) for k, v in {
            't': self._processing_time,
            'f': self._frame_num,
            'p': self._percents,
            'd': self._distance,
            'a': self._action_states,
            'g': self._gamestate,
            'm': self._menu,
            's': self.stop_tracking
        }.items()}

        super().__init__(onshutdown=onshutdown, commands=commands)

    def _continuous_wrapper(self, func):
        '''Adds continuous flag to func.
        Func must take 0 args.'''
        def f(continuous=False):
            if continuous:
                self.set_tracker(func)
            return func()
        return f

    def update(self, gamestate):
        '''Call this each frame to update recent stats.'''
        self.last_gamestate = gamestate

        # any cumulative stats
        if self.console:
            self.max_processing = max(self.max_processing, self.console.processingtime)

        # any tracker update
        if self.tracker:
            curr = self.tracker()
            if not curr == self.tracked_last:
                print(curr)
                self.tracked_last = curr

    def set_tracker(self, func):
        '''Set a function to keep printing on update.'''
        self.tracker = func
        self.tracked_last = None

    def stop_tracking(self):
        '''Don't print anything continuously.'''
        print('Stopped tracking.')
        self.tracker = None
        self.tracked_last = None

    def add_command(self, command, func, give_gamestat=False):
        '''Add custom command, adding continuous functionality.
        Gives gamestate obj if needed for a custom gamestat.
        >>> this.add_gamestat_command('m',
            lambda gamestate: 'Menu: {}'.format(gamestate.menu_state),
            give_gamestat=True)'''

        if give_gamestat:
            func = lambda: func(self.last_gamestat)
        super().add_command(command, self._continuous_wrapper(func))

    ### some useful gamestate stats/properties/getters/formatters

    def _processing_time(self):
        return 'Max bot processing time: {:.2f} ms for a frame'.format(self.max_processing)

    def _frame_num(self):
        return 'Frame num: {}'.format(self.last_gamestate.frame)

    def _percents(self):
        return 'Percents: {}%  {}%'.format(self.last_gamestate.player[1].percent,
                                           self.last_gamestate.player[2].percent)
    def _distance(self):
        return 'Distance: {:4f}'.format(self.last_gamestate.distance)

    def _action_states(self):
        return 'Action states: {}  {}'.format(self.last_gamestate.player[1].action,
                                              self.last_gamestate.player[2].action)
    def _gamestate(self):
        return 'Gamestate: {}'.format(self.last_gamestate)

    def _menu(self):
        return 'Menu: {}'.format(self.last_gamestate.menu_state)
