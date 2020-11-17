'''Wrapping melee.Button enums for easy sequences and consumption (see usage in bots).

Representing a single input - `tuple`:
    - `(True, btn, x, y)`   tilt_analog
    - !! forgot L/R, whoops. `(True, btn, float)` will likely be the format.--
    - `(True, btn)`         press_btn
    - `(False, btn)`        release_btn
    - `(False,)`            release_all
    - `()`                  no inputs this frame.

Inputs in a frame - `tuple(tuple)`:
    - `(single_input,)`
    - `(many,inputs,same,frame)`

A sequence of inputs, frame by frame - `list[tuple(tuple))]`:
```
four_frames_of_inputs = [
    ((True, Button.BUTTON_MAIN, 0.5, 0), (True, Button.BUTTON_B)),
                                    # down+b same frame
    (),                             # wait a frame
    ((True, Button.BUTTON_Y),),     # tap jump
    ((False,),)                     # all Button/sticks back to default
]
```'''

from melee import Button
import random

def make_inputs(inputs, controller):
    # press given buttons for this frame
    for press, *button_args in inputs:
        if len(button_args) > 1:    # (True, btn_stick, x, y)
            controller.tilt_analog(*button_args)
        else:
            if press:   # (True, btn)
                controller.press_button(*button_args)
            else:
                if button_args: # (False, btn)
                    controller.release_button(*button_args)
                else:   # (False,)
                    controller.release_all()
    # []  frame of nothing

def wait(n):
    '''Gives n frames of no inputs. Use * to unpack in sequence.
    >>> inputs = [
    >>>     ...,
    >>>     *wait(3),
    >>> ]

    >>> [..., (), (), (),]'''
    return [()] * n
    # return [()for _ in range(n)]

def repeat(n, *input_frames):
    '''Each arg is a frame's worth of  Use * to unpack in sequence.
    >>> inputs = [
    >>>     *repeat(2, (down, B), (un_B,)),
    >>>     *repeat(3, *jump_n_laser),
    >>> ]

    >>> [(down, B), (un_B,), (down, B), (un_B,), (jump,), (laser,), (jump,) ...]'''
    return [*input_frames] * n

# single inputs

release = (False,)
center = (True, Button.BUTTON_MAIN, 0.5, 0.5)
down = (True, Button.BUTTON_MAIN, 0.5, 0)
up = (True, Button.BUTTON_MAIN, 0.5, 1)
left = (True, Button.BUTTON_MAIN, 0, 0.5)
right = (True, Button.BUTTON_MAIN, 1, 0.5)

A = (True, Button.BUTTON_A)
B = (True, Button.BUTTON_B)
X = (True, Button.BUTTON_X)
Y = (True, Button.BUTTON_Y)
L = (True, Button.BUTTON_L)
R = (True, Button.BUTTON_R)

# taunt = (True, Button.BUTTON_D_UP)

un_A = (False, Button.BUTTON_A)
un_B = (False, Button.BUTTON_B)
un_Y = (False, Button.BUTTON_Y)
un_L = (False, Button.BUTTON_L)


### sequences

# up_B = [(B, up,)]

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
        *wait(15),
        *laser(),
        *wait(20)
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

def dashdance():
    return [
        (left,),
        (),
        (right,),
        (),
    ]
