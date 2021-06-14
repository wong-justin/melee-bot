# melee-bot

An easier way to develop a SSBM bot. Built off [libmelee](https://github.com/altf4/libmelee).

![Screen capture](./demo/demo.gif)

## Features

- Interact with gameplay: track stats, debug gamestates, control bot
- `start_game()` covers everything from Dolphin startup to _Ready, Go!_
- Bot classes let you focus on making gameplay strategies
- Simple inputs framework for making button presses and sequences

## Quickstart

#### Dolphin
- add necessary gecko codes by replacing old `dolphinpath/Sys/GameSettings/GALE01r2.ini` with [this one](https://raw.githubusercontent.com/altf4/slippi-ssbm-asm/libmelee/Output/Netplay/GALE01r2.ini)
  - I recommend keeping the original `GALE01r2.ini` around just in case
  - ... or if you haven't done so already, dedicate a second Dolphin installation for development separate from your personal playtime Dolphin.

#### Install
`pip install -e git+https://github.com/wong-justin/melee-bot.git#egg=livemelee`

#### Code
```python
# main.py
from livemelee import start_game, Bot
start_game((Bot(), Bot(), None, None))
```

#### Run
`python main.py "path/to/dolphin" "path/to/iso"`

See [demo.py](demo/demo.py) for all-around usage,
or [botless_demo.py](demo/botless_demo.py) for just hooking into gameplay.

## Docs
https://wong-justin.github.io/melee-bot/

#### Still not working?

Check the more detailed [libmelee setup instructions](https://github.com/altf4/libmelee#setup-instructions). If that doesn't help, leave an issue here if something is broken or not clear. I'm still tidying up code and documentation, which may have left out an important detail.

___

#### Todo

- [ ] Generalize for other ports and online connection
  - [ ] investigate same-char-costume port detection solution
    - [ ] generate list of processed joystick inputs ( `for .2f x,y in range(1) set_stick(x,y) -> processed_inputs_set.add(gamestate.controller(x,y))` ). Game has particular zones like that hax document showed, eg `(0.5, .6875)`, `(0.125, 0.5)`, etc
- [x] don't expose any liveinputs class but just give cmds to start_game
- [ ] investigate `cmd.Cmd` instead of argparse
- [ ] Unit tests
- [ ] Test on Linux, OSX
- [x] refactor misc tidbits as utils submodule?
  - [ ] rename bool utils with prefix `is_...()`
- [ ] Round out inputs module
  - [ ] switch arg order in repeat()
  - [ ] capitalize button constants?
- [ ] consistent args inheritance in Bots
  - [ ] is there a clean solution for inherting `__init__` signature? would like to cascade to defaults from base class
- [ ] use command line to one-time set dolphin path as local config?
- [ ] update demo gif with stat tracking
- [ ] clean up docs formatting
  - [ ] replace documentation.md with formatted docstring in livemelee__init__
    - [ ] setup script replaces docstring?
- [ ] make a framework for custom menu nav?
  - [ ] eg. to change from 4 stock to inifinite time (good for training ML)
  - [ ] or eg. move cursor to new stage icon locations in crystal melee iso
- [ ] use env variables instead of command line paths? would be nice for ipynb notebooks or other situations where command line is not available
- [ ] Make a semi-playable bot
- [ ] Sidequest - train a bot with machine learning
  - [ ] gather training dataset of replays
  - [ ] learning inputs
  - [ ] recognizing situations, eg. edgeguards
