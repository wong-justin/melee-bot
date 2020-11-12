import threading
from melee import GameState
import argparse

BREAK_FLAG = -2
EXTRA_ARGS = 'extra_args'
# CONTINUOUS_FLAG = 'continuous'

class StoreExtraArgs(argparse.Action):
    # purpose is to allow/accept/store extra inputs as function args without needing "-" flag.
    # ie. allow inputs like ">>> connect PLUP#123" or ">>> moveto 10 40"
    # extra args will later be passed to command as positional args.
    # quirks/drawbacks:
    #   - won't pass kwargs from user input to function; only positional args allowed.
    #   - args come from string (raw user input separated on spaces),
    #   so command functions taking these args need to parse types if str not desired (eg str -> int)
    #   - args can't start with "-" (RIP negatives) (it triggers parser unrecognized flag)

    def __init__(self, **kwargs):
        kwargs['nargs'] = '*'   # accept 0 or more args
        super().__init__(**kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, EXTRA_ARGS, values)
        # setattr(namespace, EXTRA_ARGS, [v if not _is_int(v) else int(v) for v in values])   # try to convert ints

# def _is_int(s):
#     # quick and dirty. I just trust that exposed user commands won't need floats or negs
#     return s.isdigit()

def _accept_any_args(func):
    # wrapper for taking args that were parsed (if any)
    return lambda args_namespace: func(*getattr(args_namespace, EXTRA_ARGS))#, default=[]))

def _print(func):
    # wrapper for printing result of a function.
    def f(*args):
        result = func(*args)
        if result == None:   # printing None does not look nice
            print('.')#done')# assure that function finished (or should we do nothing?)
        else:
            print(result)
        return result
    return f

def _separate(s):
    # emulating sys.argv with raw input string. currently ignores quotes wrapping spaces.
    return s.split(' ')

def _add_command(subparser_adder, command, details):
    '''Adds command as subparsers/subcommands so it's recognized as given -
    as positional args, no "-" flag symbol needed'''

    func, descrip = _unpack(details)
    cmd_parser = subparser_adder.add_parser(command,
                                            help=descrip,
                                            add_help=False)
    cmd_parser.set_defaults(func=_print(_accept_any_args(func)))    # set the command
    # cmd_parser.set_defaults(func=_accept_any_args(func)))
    cmd_parser.add_argument(EXTRA_ARGS, action=StoreExtraArgs)  # allow any extra inputs as args
    # cmd_parser.add_argument('-c', action='store_true', dest=CONTINUOUS_FLAG)

class LiveInputsThread(threading.Thread):
    '''Invoke functions live in shell session during gameplay.
    Similar to a command line parser.
    Used for live debugging or injecting commands to gameplay.

    Commands format: {'cmd': func} or better {'cmd': (func, 'descrip/directions')}

    Ex:
    live_thread = LiveInputsThread(     # init before starting game
        onshutdown=stop_everything,
        commands={
            'status': lambda: print(bot.status),
            'connect': lambda code: bot.direct_connect(code),
            'A': controller.press_a,
            'move': (bot.move, 'move bot [n] units in forward direction'),
        })
    [...game loop started, this thread waiting...]
    >>> connect PLUP#123
    >>> moveto 10 40
    >>> status
    >>> ...
    >>> quit'''

    def __init__(self, onshutdown, commands={}):
        '''Creates parser with given commands and starts thread awaiting input.'''
        parser = argparse.ArgumentParser(prog='',           # program name would distract
                                         description='Perform commands during gameplay.',
                                         add_help=False)    # we have custom help arg, not "-help"
        meta_commands = {
            'test': (lambda *s:'You typed {} arg(s): {}'.format(len(s), s), 'test [your] [strings] ...'),
            'help': parser.print_help,  # ideally help and quit dont get wrapped in _print and _accept_args
            'quit': lambda: BREAK_FLAG  # as happens in _add_commands
        }                               # but oh well

        subparser_adder = parser.add_subparsers()
        for command, details in {**commands, **meta_commands}.items():
            _add_command(subparser_adder, command, details)
            # type(self)._add_command(subparser_adder, command, details)   # allow subclassing?

        self.parser = parser
        self.onshutdown = onshutdown    # callback
        super().__init__(name='input-thread')
        self.start()    # save for caller to start when they want?

    def run(self):
        '''Start this thread waiting for user inputs, exiting program if asked.'''
        self.parser.print_help()

        while True: # wait for next input
            try:
                args = self.parser.parse_args(args=_separate(input()))
                # perform command
                if args.func(args) == BREAK_FLAG:
                    print('Stopping thread...')
                    break

            except SystemExit as e: # thrown whenever parser doesn't like input
                # print('Bad command:', e)
                continue
            except TypeError as e:
                print('Bad command args:', e)
                continue
            # thrown when ctrl-c interrupts hanging input() -
            # except (KeyboardInterrupt, EOFError, Exception) as e:
            #     break

        self.onshutdown()

def _unpack(details):
    # completes (func, descrip) tuple if descrip not present.
    # allows for shorter {cmd: func} usage.
    # doesnt actually unpack but it sounds nice when used in context.
    return (details if type(details) is tuple else (details, ''))

class LiveGameStats(LiveInputsThread):
    '''Enhances LiveInputsThread by incorporating stats from melee.GameState.'''
    # and adding printing-on-change feature.'''

    def __init__(self, onshutdown, commands={}, console=None):
        # init with console if you want a processing time stat

        stats = {   # stats that don't need gamestate
            'process': (self._processing_time, 'processing time'),
            'dur': (self._stock_duration, 'stock duration'),
            # 'track': (lambda cmd: self.track(cmd), 'track [cmd]'),
        }
        stats.update({cmd: ( self._with_gamestate(func), descrip )
             for cmd, (func, descrip) in {
                'f': (_frame_num, 'frame num'),
                'p': (_percents, 'percents'),
                'd': (_distance, 'distance'),
                'a': (_action_states, 'action states'),
                'g': (_gamestate, 'gamestate'),
                'm': (_menu, 'menu'),
                'stocks': (_stocks, 'stocks')
             }.items()
        })
        super().__init__(onshutdown=onshutdown, commands={**commands, **stats})

        # any persistent/cumulative stats
        self.max_processing = 0     # ms
        self.console = console      # for above
        self.stock_duration = 0     # frames, ie 1/60th sec
        self.stocks = 4             # tells when to reset above
        self.last_gamestate = None  # will provide rest of the stats

    def _with_gamestate(self, func):
        # wrapper to pass last gamestate stored in self
        return lambda: func(self.last_gamestate)

    def update(self, gamestate):
        '''Call this each frame to update recent stats.'''
        self.last_gamestate = gamestate

        # update any cumulative stats
        self._update_processing()
        if 2 in gamestate.player:
            self._update_stock_dur(gamestate)

    def _processing_time(self):
        # a cumulative stat stored in self
        return 'Max bot processing time: {:.2f} ms for a frame'.format(self.max_processing)

    def _update_processing(self):
        if self.console:
            self.max_processing = max(self.max_processing, self.console.processingtime)

    def _stock_duration(self):
        # a cumulative stat stored in self
        return '{} sec into this stock'.format(self.stock_duration // 60)   # fps

    def _update_stock_dur(self, gamestate):
        curr_stocks = gamestate.player[2].stock
        if not self.stocks == curr_stocks:
            self.stocks = curr_stocks   # -= 1
            self.stock_duration = 0
        else:
            self.stock_duration += 1

### some useful gamestate stats/properties/getters/formatters:

def _frame_num(gamestate):
    return 'Frame num: {}'.format(gamestate.frame)

def _percents(gamestate):
    return 'Percents: {}%  {}%'.format(gamestate.player[1].percent,
                                       gamestate.player[2].percent)
def _distance(gamestate):
    return 'Distance: {:4f}'.format(gamestate.distance)

def _action_states(gamestate):
    return 'Action states: {}  {}'.format(gamestate.player[1].action,
                                          gamestate.player[2].action)
def _gamestate(gamestate):
    return 'Gamestate: {}'.format(gamestate)

def _menu(gamestate):
    return 'Menu: {}'.format(gamestate.menu_state)

def _stocks(gamestate):
    return 'Stocks: {}  {}'.format(gamestate.player[1].stock,
                                   gamestate.player[2].stock)
