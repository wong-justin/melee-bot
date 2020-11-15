from bot import FalcoBot, InputsBot, ControllableBot, Bot
from interact import LiveGameStats
import melee
from patches import _Controller
import argparse
import signal
import sys

### command line starts everything

parser = argparse.ArgumentParser()
parser.add_argument('path', help='dolphin folder')
args = parser.parse_args()

### init game + connection

console = melee.Console(path=args.path)
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

# bot = FalcoBot(bot_controller)
bot = ControllableBot(bot_controller)
dummy = Bot(other_controller)

logger = melee.Logger()
live_interface = LiveGameStats(onshutdown=kill, console=console, commands={
    **bot.commands,
    'c': (lambda: _Controller(bot_controller.current), 'controller state'),  # str compares better
    'inputs': (lambda: 'Input queue: {}'.format(len(bot.queue)), 'bot input queue'),
})

### main loop

while True:
    gamestate = console.step()
    if not gamestate:
        break

    # dummy.act(gamestate)
    # bot.act(gamestate)

    live_interface.update(gamestate)
    logger.logframe(gamestate)
    logger.log('Frame Process Time', console.processingtime)   # ms
    logger.writeframe()
