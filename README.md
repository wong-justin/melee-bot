# melee-bot

An easier way to develop a SSBM bot. Enhances [libmelee](https://github.com/altf4/libmelee) experience.

## Demo
![Screen capture](./demo/demo.gif)

## Features
- Interact with gameplay: control bot, track stats, debug gamestates
- Simple inputs framework to make button presses and sequences
- Bot classes handle setup to let you focus on gameplay strategies

## Quickstart
```python
from setup import start_game
from bot import Bot
start_game((Bot(), Bot(), None, None))
```
See [demo.py](demo/demo.py) for all-around usage,
or [botless_demo.py](demo/botless_demo.py) for hooking into gameplay.

#### Todo

- [ ] Generalize for other ports and online connection
- [ ] Unit tests
- [ ] Test on Linux, OSX
- [ ] Round out inputs.py
  - [ ] switch arg order in repeat()
- [ ] CheckBot.set_timer(every, do, repeat) could sound better than (n, do, repeat)
- [ ] use command line to set dolphin path as local config?
- [ ] update demo gif
- [ ] Make a semi-playable bot
- [ ] Sidequest - train a bot with machine learning
  - [ ] gather training dataset of replays
  - [ ] learning inputs
  - [ ] recognizing situations, eg. edgeguards
