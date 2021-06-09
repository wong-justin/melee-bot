'''Create entry point to init everything and start Dolphin.'''

import argparse
import melee
from .interact import LiveGameStats

def start_game(ports, cmds={}, log=True):
    '''Main method to fully start game.
    Command-line first needs dolphin folder path, then game starts.
    ```
    # main.py
    ...
    start_game(...)
    ```
    `python main.py path/to/dolphin`

    Args:
        ports: tuple containing 4 bot instances or Nones.

            eg. `(None, my_bot, None, None)`

        cmds: optional.

            - `dict`: of custom commands {'keypress': (func, 'descrip')}.
            - default: empty dict, no custom commands
            - `None`: no live thread desired (probably for performance)

        log: `bool`, write game logs to file with `melee.Logger` if True (default)'''

    args = _start_command_line()
    console = melee.Console(path=args.path)

    # controllers must be connected before console run/connect...
    bots = _assign_controllers(ports, console)

    console.run()
    console.connect()

    # ... and connected after
    _connect_controllers(bots)

    logger = melee.Logger() if log else None

    live_interface = None
    if cmds is not None:
        live_interface = LiveGameStats(commands=cmds)
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
    # simple CLI to get dolphin folder path
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help='dolphin folder')
    return parser.parse_args()

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
