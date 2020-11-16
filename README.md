# melee-bot

An easier way to develop a SSBM bot. Built off [libmelee](https://github.com/altf4/libmelee).

## Demo
![Screen capture](./demo/demo.gif)

## Features

- Interact with gameplay: control bot, track stats, debug gamestates
- Simple inputs framework to make button presses and sequences
- Bot classes handle setup to let you focus on gameplay strategies

## Quickstart

#### Pip:
`pip install -e git+https://github.com/wong-justin/melee-bot.git#egg=melee2`

#### Code:
```python
from melee2 import start_game
from melee2.bots import Bot
start_game((Bot(), Bot(), None, None))
```
See [demo.py](demo/demo.py) for all-around usage,
or [botless_demo.py](demo/botless_demo.py) for hooking into gameplay.

___

#### Todo

- [ ] Generalize for other ports and online connection
- [ ] Unit tests
- [ ] Test on Linux, OSX
- [ ] Round out inputs.py
  - [ ] switch arg order in repeat()
- [ ] CheckBot.set_timer(every, do, repeat) could sound better than (n, do, repeat)
- [ ] use command line to set dolphin path as local config?
- [ ] update demo gif with stat tracking
- [ ] Make a semi-playable bot
- [ ] Sidequest - train a bot with machine learning
  - [ ] gather training dataset of replays
  - [ ] learning inputs
  - [ ] recognizing situations, eg. edgeguards
