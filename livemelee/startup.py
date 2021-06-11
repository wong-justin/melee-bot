'''Create entry point to init everything and start Dolphin.'''

import argparse
# import sys
from pathlib import Path
import melee
from .interact import LiveInputsThread

def start_game(ports, cmds={}, log=True):
    '''Main method to fully start game.
    Command-line first needs dolphin path and iso path, then game starts.
    Iso path is optional if you have a default iso set to run on Dolphin startup.
    ```
    # main.py
    ...
    start_game(...)
    ```
    `python main.py path/to/dolphin path/to/iso`

    Args:
        ports: tuple containing 4 bot instances or Nones.

            eg. `(None, my_bot, None, None)`

        cmds: optional.

            - `dict`: of custom commands `'cmd': (func, 'descrip')` or `'cmd': func`.
            - default: empty dict, no custom commands
            - `None`: no live thread desired (probably for performance)

        log: `bool`, write game logs to file with `melee.Logger` if True (default)'''

    args = _start_command_line()
    dolphin_folder = str( Path(args.dolphin_path).parent )
    console = melee.Console(path=dolphin_folder) # libmelee wants the folder

    # controllers must be connected before console run/connect...
    bots = _assign_controllers(ports, console)

    console.run(iso_path=args.iso_path) # if None, relies on default Dolphin iso on startup
    console.connect()

    # ... and then controllers are connected afterward
    _connect_controllers(bots)

    logger = melee.Logger() if log else None

    live_interface = None
    if cmds is not None:
        live_interface = LiveInputsThread(commands=cmds)
        live_interface.onshutdown = _shutdown(console, logger)
        live_interface.start()

    while True:

        gamestate = console.step()
        if not gamestate:
            break

        for bot in bots:
            bot.act(gamestate)

        if live_interface:
            live_interface.update(gamestate)

        if logger:
            logger.logframe(gamestate)
            logger.log('Frame Process Time', console.processingtime)   # ms
            logger.writeframe()

def _start_command_line():
    # simple CLI to get paths for dolphin and optionally iso

    parser = argparse.ArgumentParser()
    parser.add_argument('paths', nargs='+', help='dolphin/path [iso/path]')
    args = parser.parse_args()
    args.dolphin_path = args.paths[0]
    args.iso_path = args.paths[1] if len(args.paths) > 1 else None
    return args

def _assign_controllers(ports, console):
    # make + give controllers to any bots present in 4-tuple of ports
    bots = []
    for port, bot in enumerate(ports):
        if bot:
            controller = melee.Controller(console=console, port=port+1)
            # controller = melee.Controller(console=console, port=port+1, type=melee.ControllerType.STANDARD)
            bot.controller = controller
            bots.append(bot)
    return bots

def _connect_controllers(bots):
    for bot in bots:
        bot.controller.connect()

def _shutdown(console, logger):
    # returns callable that closes dolphin and anything else
    def f():
        console.stop()
        if logger:
            print()
            logger.writelog()
            print('Log file created: ' + logger.filename)
        print('Shutting down')
    return f
