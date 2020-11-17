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
- [ ] Unit tests
- [ ] Test on Linux, OSX
- [ ] Round out inputs module
  - [ ] switch arg order in repeat()
- [ ] use command line to set dolphin path as local config?
- [ ] update demo gif with stat tracking
- [ ] clean up docs formatting
  - [ ] move documentation.md out of package? makes sense but low priority
- [ ] Make a semi-playable bot
- [ ] Sidequest - train a bot with machine learning
  - [ ] gather training dataset of replays
  - [ ] learning inputs
  - [ ] recognizing situations, eg. edgeguards
