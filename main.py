import melee
from bot import MyBot, Bot
from livelogging import LiveInputsThread
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
other_controller = melee.Controller(console=console, port=1)    # dummy to proceed to game, replacing human for now

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
    
logger = melee.Logger()
live_logger = LiveInputsThread(console=console, onshutdown=kill)

bot = MyBot(bot_controller)
dummy = Bot(other_controller)

### main loop

while True:
    gamestate = console.step()
    if not gamestate:
        break
            
    bot.act(gamestate)
    dummy.act(gamestate)
        
    live_logger.update(gamestate)
    logger.logframe(gamestate)
    logger.log('Frame Process Time', console.processingtime)   # ms
    logger.writeframe()
        