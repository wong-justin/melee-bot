
This package aims to make a simpler API around `libmelee` and make it easier to start implementing your gameplay ideas.


## Before you start

Make sure you follow the brief [setup](https://github.com/wong-justin/melee-bot#quickstart) outlined in the repo - mostly just be sure to have the necessary gecko codes for Dolphin. If you still can't run the quick example, leave an issue on github.

## Quick Example
```python
# main.py
from livemelee import start_game, Bot
start_game((Bot(), Bot(), None, None))
```

`python main.py "path/to/dolphin/" "path/to/iso"`

## Less trivial example, a breakdown
A typical development case might look like:

- Create a bot and implement its main loop method:

```python
# from livemelee import InputsBot
class MyBot(InputsBot):

    def check_frame(self, gamestate):
        if gamestate.frame % 120 == 0:
            self.make_some_inputs()
```
- ... by telling it when to make what inputs:

```python
# from livemelee.inputs import *
    def make_some_inputs(self):
        self.queue = [
            (down,),
            (B,),
            (release,),
            *wait(5),
            *taunt(),
        ]
```
- Define some commands for the interactive thread:

```python
bot = MyBot()

commands = {
    'i': (bot.set_some_inputs, 'make inputs now'),
    'next': (lambda: bot.queue[0], 'print next input queued'),
}
```
- Put bots in ports and start:

```python
# from livemelee import start_game
start_game((None, bot, None, None), commands)
```
- Run on command line, passing dolphin path and iso path: `python main.py "path/to/dolphin/executable" "path/to/ssbm/iso"`


## Components of `livemelee`
- `start_game` - function handling Dolphin startup to get in-game
- Different `Bot` classes to use or extend
- `inputs` module - framework for pressing buttons
- `utils` module - misc, eg. pretty prints


## A deeper look

Behind the scenes, `start_game` implements Dolphin startup with libmelee.
Additionally, you pass objects (bots) in the "ports" so they can get a controller and access the game state. It looks something like this:

```python
# essentially in start_game(bot, None, None, None):

bot.controller = Controller()
...
while True:
  gamestate = dolphin.next_frame()
  bot.act(gamestate)
```

You could pass in something besides a bot if you just want access to the gamestate.
Eg: humans play in ports 1,2 so a realtime parser in port 3 or 4 can make callbacks according to in-game triggers.

The base class `Bot` implements `act` with menu navigation (from libmelee) so only `play_frame` is to be implemented for actual gameplay. Other `Bot` subclasses scaffold off that, such as how `InputsBot` gives you `check_frame` so you can `perform` inputs.

___

The other feature of `start_game` is realtime commands. After `start_game` is called and opens Dolphin, a thread is opened in your terminal for typing commands. There's two default commands: `help`, which shows available commands, and `quit`, which closes the thread and Dolphin. You can make new commands with the format `command: function` or `command: (function, description)`. The result of `function()` is printed when `command` is entered.

Notes on commands:

- After executing a command, a period `.` is printed on a newline as a visual confirmation.
- You could make a command function that takes multiple args. eg.  
`>>> cmd a b 10` would call `func_for_cmd('a','b','10')`  
But there's limitations because of `argparse`:

    - args can't start with "-" (RIP negatives) (because it triggers parser unrecognized flag)
    - args will always be strings

- `quit` causes some not-so-pretty error output, but Dolphin still closes fine.
- `Ctrl-C` keyboard interrupt won't close cleanly (Dolphin will stay open). You should only use the `quit` command.

___

Notes on running the script:
- example: `python main.py "melee\stuff\FM-Slippi-2.3.0-Win\FM-Slippi\Slippi Dolphin.exe" "melee\stuff\Super Smash Bros. Melee (USA) (En,Ja) (v1.02).iso"
`
- Dolphin path is to the executable, as opposed to the containing folder that libmelee wants. (I think it feels more intuitive this way)
- ISO path is optional if you have a default iso set to run on Dolphin startup
- Recommended - copy this command into a little script for quick reference in your working directory, eg. `run.bat`


## More
Only offline play is supported for now, mainly assuming ports 1 + 2. Soon to change!

Read up on the API that `livemelee` wraps around: [libmelee](https://github.com/altf4/libmelee)
- get to know [GameState](https://libmelee.readthedocs.io/en/latest/gamestate.html), [PlayerState](https://libmelee.readthedocs.io/en/latest/gamestate.html#melee.gamestate.PlayerState), Controller, etc.
