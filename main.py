from bot import FalcoBot, Bot
from liveinputs import LiveGameStats
import melee
import argparse
import signal
import sys

### command line starts everything

parser = argparse.ArgumentParser(description='Example of libmelee in action')

parser.add_argument('--dolphin_executable_path', '-e', default=None,
                    help='The directory where dolphin is')

args = parser.parse_args()

### init game + connection

console = melee.Console(path=args.dolphin_executable_path)

bot_controller = melee.Controller(console=console, port=2)
other_controller = melee.Controller(console=console, port=1)    # dummy only to proceed past menu, replacing human for now

console.run()
console.connect()
bot_controller.connect()
other_controller.connect()

### misc helpers, inits

def kill():
    '''Close Dolphin and anything else.'''
    console.stop()
    logger.writelog()

    print()
    print('Log file created: ' + logger.filename)
    print('Shutting down cleanly...')
    sys.exit(0)

signal.signal(signal.SIGINT, lambda sig, frame: kill())  # on ctrl-c interrupt

bot = FalcoBot(bot_controller)
dummy = Bot(other_controller)

logger = melee.Logger()
live_logger = LiveGameStats(onshutdown=kill, console=console)
live_logger.add_command('c',
    lambda: 'Controller: {}'.format(bot_controller.current))
live_logger.add_command('left', lambda: bot_controller.tilt_analog(melee.enums.Button.BUTTON_MAIN, 0, 0.5))
#live_logger.add_command('b', bot.toggle_debug)
#live_logger.add_command('n', bot.to_next_strategy)

#def control_bot_live():
#    buttons = {
#        'l': melee.enums.Button.BUTTON_L,
#        'r': melee.enums.Button.BUTTON_R,
#        'a': melee.enums.Button.BUTTON_A,
#        'start': melee.enums.Button.BUTTON_START
#    }
#    for cmd, val in buttons.items():
#        live_logger.add_command('press ' + cmd, lambda: bot_controller.press_button(val))
#        live_logger.add_command('unpress ' + cmd, lambda: bot_controller.release_button(val))
#
#
#    live_logger.add_command('release', bot_controller.release_all)
#
#    for cmd, func in live_logger.commands.items():
#        print(cmd, '\t', func)
#
#control_bot_live()

### main loop

while True:
    gamestate = console.step()
    if not gamestate:
        break

    dummy.act(gamestate)
    bot.act(gamestate)

    live_logger.update(gamestate)
    logger.logframe(gamestate)
    logger.log('Frame Process Time', console.processingtime)   # ms
    logger.writeframe()
