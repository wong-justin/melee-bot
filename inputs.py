'''Wrapping melee.Button enums for easy sequences and consumption (see bots).
Options/formats:
(True, btn, x, y)   tilt_analog
(True, btn)         press_btn
(False, btn)        release_btn
(False,)            release_all
[]                  no inputs this frame
Usage:
>>> four_frames_inputs = [
    ((True, Button.BUTTON_MAIN, 0.5, 0), (True, Button.BUTTON_B)),
                                    # down+b same frame
    [],                             # wait a frame
    ((True, Button.BUTTON_Y),),    # jump input
    ((False,),)                     # all Button/sticks back to default
]'''

from melee import Button
import random

# convenience

def wait(n):
    '''Gives n frames of no  Use * to unpack in sequence.
    >>> inputs = [
        ...,
        *wait(42),
    ]
    >>> [..., [], [], [],]'''
    return [[]] * n
    # return [[] for _ in range(n)]

def repeat(n, *input_frames):
    '''Each arg is a frame's worth of  Use * to unpack in sequence.
    >>> inputs = [
        *repeat(2, (down, B), (un_B,)),
        *repeat(3, *jump_n_laser),
    ]
    >>> [(down, B), (un_B,), (down, B), (un_B,), (jump,), (laser,), (jump,) ...]'''
    return [*input_frames] * n

release = (False,)
center = (True, Button.BUTTON_MAIN, 0.5, 0.5)
down = (True, Button.BUTTON_MAIN, 0.5, 0)
up = (True, Button.BUTTON_MAIN, 0.5, 1)
left = (True, Button.BUTTON_MAIN, 0, 0.5)
right = (True, Button.BUTTON_MAIN, 1, 0.5)

A = (True, Button.BUTTON_A)
un_A = (False, Button.BUTTON_A)
B = (True, Button.BUTTON_B)
un_B = (False, Button.BUTTON_B)
Y = (True, Button.BUTTON_Y)
un_Y = (False, Button.BUTTON_Y)
L = (True, Button.BUTTON_L)
un_L = (False, Button.BUTTON_L)

# up_B = (B, up)


# class Sequences:
# which would be faster,
#   make these all functions-
#       def f(): return [.....]
#   or copy in user class-
#       class ... def f(): self.queue = somedeepcopy(sequence_ref) ?
# i think first option

def laser():
    return [
        (B,),
        (un_B,)
    ]

def shorthop():
    return [
        (Y,),
        (un_Y,),
    ]

def fastfall():
    return [
        (down,),
        (center,),
    ]

def jump_n_laser():
    return [
        *shorthop(),
        *wait(5),
        *laser(),
    ]

def fastfall_laser():
    return [
        *shorthop(),
        *wait(3),
        (B,),
        (un_B, down,),
        *wait(5),
        (center,),
    ]

# crude
def fastfall_laser_rand():
    pre = random.randint(2,4)#10)
    post = random.randint(1,5)
    return [
        *shorthop(),
        *repeat(pre, *fastfall()),
        *laser(),
        *repeat(post, *fastfall()),      # fastfall enough til ground; queue should be reset anyways
        *wait(5),           # actually uneccessary inputs could be buffered and mess up the future
    ]                   # get a more precise sequence

def taunt():
    return [
        ((True, Button.BUTTON_D_UP),),
        ((False, Button.BUTTON_D_UP),)
    ]

def shield():
    return [
        (L,),
        *wait(10),
        (un_L,),
    ]
