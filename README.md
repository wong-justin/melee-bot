# melee-bot

An easier way to develop a SSBM bot. Built off [libmelee](https://github.com/altf4/libmelee).

![Screen capture](./demo/demo.gif)

## Features

- Interact with gameplay: track stats, debug gamestates, control bot
- `start_game()` covers everything from Dolphin startup to Ready, Go!
- Bot classes let you focus on making gameplay strategies
- Simple inputs framework for making button presses and sequences

## Quickstart

#### Install
`pip install -e git+https://github.com/wong-justin/melee-bot.git#egg=livemelee`

#### Code
```python
# main.py
from livemelee import start_game, Bot
start_game((Bot(), Bot(), None, None))
```

#### Run
`python main.py "path/to/dolphin/folder"`

See [demo.py](demo/demo.py) for all-around usage,
or [botless_demo.py](demo/botless_demo.py) for just hooking into gameplay.

## Docs
https://wong-justin.github.io/melee-bot/

___

#### Todo

- [ ] Generalize for other ports and online connection
  - [ ] investigate same-char-costume port detection solution
    - [ ] generate list of processed joystick inputs ( `for .2f x,y in range(1) set_stick(x,y) -> processed_inputs_set.add(gamestate.controller(x,y))` ). Game has particular zones like that hax document showed, eg `(0.5, .6875)`, `(0.125, 0.5)`, etc
- [ ] Unit tests
- [ ] Test on Linux, OSX
- [x] refactor misc tidbits as utils submodule?
  - [ ] rename bool utils with prefix `is_...()`
- [ ] Round out inputs module
  - [ ] switch arg order in repeat()
  - [ ] capitalize button constants?
- [ ] consistent args inheritance in Bots
  - [ ] is there a clean solution for inherting `__init__` signature? would like to cascade to defaults from base class
- [ ] use command line to set dolphin path as local config?
- [ ] update demo gif with stat tracking
- [ ] clean up docs formatting
  - [ ] replace documentation.md with formatted docstring in livemelee__init__
- [ ] Make a semi-playable bot
- [ ] Sidequest - train a bot with machine learning
  - [ ] gather training dataset of replays
  - [ ] learning inputs
  - [ ] recognizing situations, eg. edgeguards
