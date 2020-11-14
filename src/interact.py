import threading
import argparse
from patches import _Gamestat

BREAK_FLAG = -2
EXTRA_ARGS = 'extra_args'
# CONTINUOUS_FLAG = 'continuous'

class StoreExtraArgs(argparse.Action):
    '''Purpose is to store any extra inputs beyond initial command
    as function args without needing any "-" flags.
    Allows inputs like:
    >>> connect PLUP#123 or >>> moveto 10 40
    as opposed to default parser behavior:
    >>> connect -specific_flag PLUP#123 or >>> moveto -other_flag 10 40

    Extra args will later be passed to command as positional args
    eg. >>> cmd a b 10   ->   func_for_cmd('a','b','10')
    Quirks/drawbacks to this style/implementation:
      - no kwargs allowed (too messy to implement anyways); only positional args.
      - args can't start with "-" (RIP negatives) (it triggers parser unrecognized flag)
      - args come from string (raw user input separated on spaces),
      so command functions taking these args need to parse strs (eg str -> int)
      - no helpful parser checking/catching/help messages on error for these extra args
      (throws type errors or other) (as opposed to intended parser use, like on initial commands)'''

    def __init__(self, **kwargs):
        kwargs['nargs'] = '*'   # accept 0 or more args
        super().__init__(**kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, EXTRA_ARGS, values)

def _accept_any_args(func):
    # wrapper for taking args that were parsed (if any)
    return lambda args_namespace: func(*getattr(args_namespace, EXTRA_ARGS))#, default=[]))

def _print(func):
    # wrapper for printing before returning result of a function.
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
    '''Adds command as subparser/subcommand sharing first input position.
    Subcommands won't need "-" flag symbol.'''

    func, descrip = _unpack(details)
    cmd_parser = subparser_adder.add_parser(command,
                                            help=descrip,
                                            add_help=False)
    cmd_parser.set_defaults(func=_print(_accept_any_args(func)))    # set the command
    # cmd_parser.set_defaults(func=_accept_any_args(func)))
    cmd_parser.add_argument(EXTRA_ARGS, action=StoreExtraArgs)  # allow any extra inputs as args

class LiveInputsThread(threading.Thread):
    '''Invoke functions in a shell session during gameplay.
    Similar to a command line parser but streamlined experience, no flags.
    Used for live debugging or injecting commands to gameplay.
    Commands should not print anything themselves - just return string/data, if anything.

    Commands format: {'cmd': func} or better {'cmd': (func, 'descrip/directions')}

    Ex:
    live_thread = LiveInputsThread(         # init before starting game
        onshutdown=stop_everything,
        commands={
            'status': lambda: bot.status,
            'connect': (bot.direct_connect, 'direct connect to [code]'),
            'A': controller.press_a,
            'moveto': (bot.move, 'move bot to [x] [y] coords'),
            'seq': (bot.loop_inputs, 'repeat custom inputs '\
                '... [a/b/x/y/l/r/z] [up/down/left/right] [release] [n wait]'),
        })
    [...game loop started, this thread waiting...]
    >>> connect PLUP#123
    >>> moveto 10 40
    >>> status
    >>>   Bot status: ...
    >>> seq b down 3 y release
    >>> quit'''

    def __init__(self, onshutdown, commands={}):
        '''Creates parser with given commands and starts thread awaiting input.'''
        parser = argparse.ArgumentParser(prog='',           # program name would distract
                                         description='Perform commands during gameplay.',
                                         add_help=False)    # we have custom help arg, not "-help"
        meta_commands = {
            'test': (lambda *s:'You typed {} arg(s): {}'.format(len(s), s), 'test [your] [strings] [...]'),
            'help': parser.print_help,  # ideally help and quit dont get wrapped in _print and _accept_args
            'quit': lambda: BREAK_FLAG  # as happens in _add_commands
        }                               # but oh well

        subparser_adder = parser.add_subparsers()
        for command, details in {**commands, **meta_commands}.items():
            _add_command(subparser_adder, command, details)
            # type(self)._add_command(subparser_adder, command, details)   # allow subclassing?

        self.parser = parser
        self.onshutdown = onshutdown    # callable
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
    # completes (func, descrip) if descrip not present in details tuple.
    # amends short command {cmd: func} in commands dict.
    # doesnt technically unpack here but it sounds nice when used in context.
    return (details if type(details) is tuple else (details, ''))

class LiveGameStats(LiveInputsThread):
    '''Enhances LiveInputsThread by incorporating stats from melee.GameState
    and adding stat-tracking / printing-on-change feature.

    >>> track p
    >>> Percents: 0%  0%
    >>> Percents: 3%  0%
    >>> Percents: 3%  16%
    >>> notrack
    >>> .
    >>> a
    >>> Action states: Action.CROUCHING  Action.LANDING'''

    def __init__(self, onshutdown, commands={}, console=None):
        # init with console if you want a processing time stat

        stats = {   # don't need gamestate
            'track': (self._track, 'print updates to [cmd]'),
            'untrack': (self._reset_tracker, 'stop tracking that'),
            'process': (self._processing_time, 'processing time'),
            'dur': (self._stock_duration, 'this stock duration'),
        }
        stats.update({cmd: ( self._with_gamestate(func), descrip )
             for cmd, (func, descrip) in {
                'f': (_Gamestat.frame_num, 'frame num'),
                'p': (_Gamestat.percents, 'percents'),
                'd': (_Gamestat.distance, 'distance'),
                'a': (_Gamestat.actions, 'action states'),
                'g': (_Gamestat.gamestate, 'gamestate'),
                'm': (_Gamestat.menu, 'menu'),
                'stocks': (_Gamestat.stocks, 'stocks'),
             }.items()
        })
        commands.update(stats)
        self.commands = commands
        super().__init__(onshutdown=onshutdown, commands=commands)

        # any persistent/cumulative stats
        self._max_processing = 0     # ms
        self._console = console      # for above
        self._stock_duration = 0     # frames
        self._stocks = 4             # tells when to reset above
        self._last_gamestate = None  # will provide rest of the stats

        self._tracker = None        # callable, called each frame
        self._tracked_last = None   # from above

    def _with_gamestate(self, func):
        # wrapper to pass last gamestate stored in self
        return lambda: func(self._last_gamestate)

    def update(self, gamestate):
        '''Call this each frame with new gamestate to update recent stats.'''
        self._last_gamestate = gamestate

        # update any cumulative stats
        self._update_processing()
        if 2 in gamestate.player:   # game started
            self._update_stock_dur(gamestate)

        if self._tracker:
            curr = self._tracker()
            if not curr == self._tracked_last:
                self._tracked_last = curr
                print(curr)

    def _reset_tracker(self):
        self._tracker = None
        self._tracked_last = None

    def _track(self, cmd):
        # check cmd func each frame for change. func must takes 0 args.
        # if custom func needs gamestate, consider wrapping _with_gamestate(func)?
        func, _ = _unpack(self.commands[cmd])
        self._tracker = func

    # for specific stats

    def _processing_time(self):
        # a cumulative stat stored in self
        return 'Max bot processing time: {:.2f} ms for a frame'.format(self._max_processing)

    def _update_processing(self):
        if self._console:
            self._max_processing = max(self._max_processing, self._console.processingtime)

    def _stock_duration(self):
        # a cumulative stat stored in self
        return '{} sec into this stock'.format(self._stock_duration // 60)   # 60 fps

    def _update_stock_dur(self, gamestate):
        curr_stocks = gamestate.player[2].stock
        if not self._stocks == curr_stocks: # reset on new stock
            self._stocks = curr_stocks      # -= 1
            self._stock_duration = 0
        else:                               # add another 1/60th sec
            self._stock_duration += 1