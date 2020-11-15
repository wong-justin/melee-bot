# melee-bot

An easier way to develop a SSBM bot. Enhances [libmelee](https://github.com/altf4/libmelee) experience.

## Demo
![Screen capture](./demo/demo.gif)

## Features
- Interact with gameplay: control bot, track stats, debug gamestates
- Simple inputs framework to make button presses and sequences
- Bot classes handle setup to let you focus on gameplay strategies

### Todo

- [ ] Test on Linux, OSX
- [ ] Generalize for other ports and online connection
- [ ] Unit tests
- [ ] Create command line options for starting the game
eg. `-bot [class] -port [1] -bot [another] -port [2]`
- [ ] Round out inputs.py
- [ ] Make a semi-playable bot
- [ ] Sidequest - train a bot with machine learning
  - [ ] gather training dataset of replays
  - [ ] learning inputs
  - [ ] recognizing situations, eg. edgeguards
