'''Group of functions returning helpful stats, given melee.Gamestate.

Two kinds:
    conditions returning bools, and
    pretty printers returning strings.

These would be nice additions to melee.Gamestate,
but we make do with this patchy submodule.

>>> stat_output = Stat.func(real_gamestate_obj)'''

from melee import Menu, Action  # enums


### conditions
# todo: replace hard coded ports

def in_game(g):
    return g.menu_state in (Menu.IN_GAME, Menu.SUDDEN_DEATH)

# def not_lasering(gamestate):
#     # just for standing, no aerial actions
#     return not gamestate.player[2].action in (Action.LASER_GUN_PULL,
#                                               Action.NEUTRAL_B_CHARGING,
#                                               Action.NEUTRAL_B_ATTACKING)
def not_taunting(gamestate):
    return not gamestate.player[2].action in (Action.TAUNT_LEFT,
                                              Action.TAUNT_RIGHT)
def grounded(gamestate):
    return gamestate.player[2].on_ground

### pretty printing


def gamestate(g):
    return 'Gamestate: {}'.format(g)

def frame_num(g):
    return 'Frame num: {}'.format(g.frame)

def menu(g):
    return 'Menu: {}'.format(g.menu_state)

def distance(g):
    return 'Distance: {:4f}'.format(g.distance)

def percents(g):
    return 'Percents: {}%  {}%'.format(g.player[1].percent,
                                     g.player[2].percent)

# def percents(g, my_port, other_port):
#     return 'Percents: {}%  {}%'.format(g.player[my_port].percent,
#                                        g.player[other_port].percent)

def actions(g):
    return 'Action states: {}  {}'.format(g.player[1].action,
                                        g.player[2].action)
def stocks(g):
    return 'Stocks: {}  {}'.format(g.player[1].stock,
                                 g.player[2].stock)
