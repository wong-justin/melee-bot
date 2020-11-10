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
for command, func in {
        'c': lambda: str(bot_controller.current),   # str compares better for tracking
        'release': lambda: bot_controller.release_all(),
        # 'left': lambda: bot_controller.tilt_analog(melee.enums.Button.BUTTON_MAIN, 0, 0.5),
        # 'l': lambda: bot_controller.press_button(melee.enums.Button.BUTTON_L),
        # 'r': lambda: bot_controller.press_button(melee.enums.Button.BUTTON_R),
        # 'A': lambda: bot_controller.press_button(melee.enums.Button.BUTTON_A),
        # 'start': lambda: bot_controller.press_button(melee.enums.Button.BUTTON_START),
        'inputs': lambda: 'Input queue: {}'.format(len(bot.queue)),
        'laser': bot.set_standing_laser_strat,
        'shlaser': bot.set_shorthop_laser_strat,
        'jump': bot.jump,
        'taunt': bot.taunt_asap,
        'rage': bot.ragequit,
        'j': lambda: bot.jumped,
    }.items():
    live_logger.add_command(command, func)

# live_logger.add_command('c', lambda: str(bot_controller.current))
# live_logger.add_command('release', lambda: bot_controller.release_all())
# live_logger.add_command('left', lambda: bot_controller.tilt_analog(melee.enums.Button.BUTTON_MAIN, 0, 0.5))
# live_logger.add_command('l', lambda: bot_controller.press_button(melee.enums.Button.BUTTON_L))
# live_logger.add_command('r', lambda: bot_controller.press_button(melee.enums.Button.BUTTON_R))
# live_logger.add_command('a', lambda: bot_controller.press_button(melee.enums.Button.BUTTON_A))
# live_logger.add_command('start', lambda: bot_controller.press_button(melee.enums.Button.BUTTON_START))
# live_logger.add_command('taunt', bot.taunt)
# live_logger.add_command('rage', bot.ragequit)
# live_logger.add_command('b', lambda: len(bot.sequence))

live_logger.start()

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
