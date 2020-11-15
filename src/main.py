from bot import FalcoBot, InputsBot, ControllableBot, CheckBot, Bot
from interact import LiveGameStats
from patches import _Controller
from setup import start_game

bot = ControllableBot()
dummy = Bot()
live_interface = LiveGameStats(commands={
    **bot.commands,
    'c': (lambda: _Controller(bot.controller.current), 'controller state'),  # str compares better
    'inputs': (lambda: 'Input queue: {}'.format(len(bot.queue)), 'bot input queue'),
})

start_game((dummy, bot, None, None), live_interface=live_interface)
