## Quick Example
```python
# main.py
from livemelee import start_game, Bot
start_game((Bot(), Bot(), None, None))
```
`python main.py "path/to/dolphin/folder"`

## Importable from `livemelee`
- `start_game` - function handles Dolphin startup to get in-game
- `LiveInputsThread`, `LiveGameStats` - manage user commands during gameplay
- `Stat` - submodule with conditions and pretty prints for `melee.GameState`
- `Inputs` - submodule holding buttons + sequence constants, and helper funcs
- `Bot`, `InputsBot`, `CheckBot`, `ControllableBot` - some bot classes to use or extend
- `buttons` - extra debugging features for `melee.ControllerState`

## General flow
1. Create a bot and implement its main loop method:

```python
class MyBot(InputsBot):

    def check_frame(self, gamestate):
        if gamestate.frame % 120 == 0:
            self.make_some_inputs()
```
2. ... by telling it when to make what inputs:

```python
    def make_some_inputs(self):
        self.queue = [
            (down,),
            (B,),
            (release,),
            *wait(5),
            *taunt(),
        ]
```
3. Init an interactive thread with custom commands:

```python
live_interface = LiveGameStats(commands={
    'i': (bot.set_some_inputs,
          'make inputs now'),
    'msg': (lambda: 'a message',
          'print a message'),
    'next': (lambda: bot.queue[0],
             'next input queued'),
})
```
4. Put bots in ports and give interactive thread:

```python
start_game((None, MyBot(), None, None),
           live_interface=live_interface)
```
5. Run on command line, passing dolphin path: `python main.py "path/to/dolphin/folder"`


## More
Only offline play is supported for now, mainly assuming ports 1 + 2. Soon to change!

Read up on the API used, [libmelee](https://github.com/altf4/libmelee): getting frame info from Gamestate, etc.
