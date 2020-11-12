import threading
from melee import GameState
import argparse

BREAK_FLAG = -2
EXTRA_ARGS = 'extra_args'

def _is_int(s):
    # quick and dirty. I just trust that exposed user commands won't need floats or negs
    return s.isdigit()

def _pass_args(func):
    # wrapper for accepting any args that were parsed
    return lambda args: func(*getattr(args, EXTRA_ARGS))#, default=[]))
    # def f(args_namespace):
    #     args = getattr(args_namespace, EXTRA_ARGS)
    #     func(*args)
    # return f

class StoreExtraArgs(argparse.Action):
    # purpose is to accept + store any function args without needing "-" flag.
    # extra args will later be passed to command as positional args.

    def __init__(self, **kwargs):
        kwargs['nargs'] = '*'   # accept >= 0 args
        super().__init__(**kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, EXTRA_ARGS, values)
        # setattr(namespace, EXTRA_ARGS, [v if not _is_int(v) else int(v) for v in values])   # try to convert ints

def test_func(s):
    s = 'Input string: ' + s
    print(s)

def _separate(s):
    # emulating sys.argv. currently ignores quotes wrapping spaces.
    return s.split(' ')

class LiveInputsThread(threading.Thread):
    '''Invoke functions live in shell session. Similar to a command line parser.
    Used for live debugging or injecting commands to gameplay.

    Ex:
    live_thread = LiveInputsThread(     # init before starting game
        onshutdown=stop_everything,
        commands={
            'a', controller.press_a,
            'move', lambda d: bot.move(d)
            'status', lambda: print(bot.status),
            'connect', lambda code: bot.direct_connect(code),
        })
    >>> ...game loop started, this thread waiting...
    >>> connect PLUP#123
    >>> move 10'''

    def __init__(self, onshutdown, commands={}):
        '''Creates parser with given commands and starts thread awaiting input.'''
        parser = argparse.ArgumentParser(prog='',           # program name would distract
                                         description='Perform commands during gameplay.',
                                         add_help=False)    # we have custom help arg, not "-help"
        meta_commands = {
            'test': (test_func, 'for testing purposes'),
            'help': parser.print_help,
            'quit': lambda: BREAK_FLAG
        }
        # add commands as subparsers so they're recognized simply as given
        #   (positional args, no "-" flag symbol needed)
        subparsers = parser.add_subparsers()    # obj for adding subparsers
        for command, details in {**commands, **meta_commands}.items():
            # unpack if description is included
            func, descrip = (details if type(details) is tuple else (details, ''))
            cmd_parser = subparsers.add_parser(command,
                                               help=descrip,
                                               add_help=False)
            cmd_parser.set_defaults(func=_pass_args(func))      # do the command (even with no args)
            cmd_parser.add_argument(EXTRA_ARGS, action=StoreExtraArgs)  # take any extra args
            # cmd_parser.add_argument('-c', action='store_true')  # continuous flag

        self.parser = parser
        self.onshutdown = onshutdown    # callback
        super().__init__(name='input-thread')
        self.start()

    def run(self):
        '''Start this thread waiting for user inputs, exiting program if asked.'''
        self.parser.print_help()

        while True: # wait for next input
            try:
                args = self.parser.parse_args(args=_separate(input()))
                # print(vars(args))#

                # perform commands
                if args.func(args) == BREAK_FLAG:
                    print('Stopping thread...')
                    break

            # except KeyboardInterrupt:   # pass to eventually onshutdown, which I could just do here...
            #     # break
            #     self.onshutdown()
            #     return
            except SystemExit as e: # thrown whenever parser doesn't accept input
                print(e)
                continue
            except TypeError as e:
                print('Bad command args:', e)
                continue
            # except (Exception, EOFError) as e:   # thrown when ctrl-c interrupts input()
            #     break

        self.onshutdown()

def _print(func):
    # wrapper for printing result of a function
    def f(*args):
        result = func(*args)
        if result == None:   # nicer looking message replacement
            print('done')
        else:
            print(result)
        return result
    return f

class LiveGameStats(LiveInputsThread):
    '''Enhances LiveInputsThread by adding updating/tracking feature
    and incorporating stats from melee.GameState.'''

    def __init__(self, onshutdown, console=None, commands={}):
        self.max_processing = -1    # a persistent/cumulative stat
        self.console = console      # for above
        self.last_gamestate = None  # will provide rest of the stats

        self.tracker = None         # a function to check for updates
        self.tracked_last = None    # last tracker() value

        new = {k: _print(v) for k, v in {
            't': self._processing_time,
            'f': self._frame_num,
            'p': self._percents,
            'd': self._distance,
            'a': self._action_states,
            'g': self._gamestate,
            'm': self._menu,
            's': self.stop_tracking
        }.items()}

        super().__init__(onshutdown=onshutdown, commands={**commands, **new})

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
