'''Create entry point to init everything and start Dolphin.'''

import argparse
import melee
from .interact import LiveGameStats

def start_game(ports, live_interface=LiveGameStats(), log=True):
    '''Main method to fully start game.
    Command-line first needs dolphin folder path, then game starts with args:

    Args:
        ports: tuple containing 4 bot instances or Nones.

            eg. `(None, my_bot, None, None)`

        live_interface: optional.

            - `LiveInputsThread`: externally initialized with custom commands.
            Don't worry about onshutdown; it will be taken care of in this method.
            - `None`: no live thread desired (probably for performance)
            - default: new `LiveGameStats`

        log: bool, write game logs to file with `melee.Logger` if True (default)'''

    args = _start_command_line()
    console = melee.Console(path=args.path)
    console.run()
    console.connect()

    bots = _assign_controllers(ports, console)

    logger = melee.Logger() if log else None

    if live_interface:
        # whether given or default, no shutdown provided yet (needs console)
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
            bot.controller = controller
            bots.append(bot)
    return bots

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
