import melee
from melee import enums
import random
import time

class Bot:
    '''Decision maker for controller inputs.
    Offline only implementation currently.'''

    def __init__(self, controller, 
                 character=melee.Character.FOX,
                 stage=melee.Stage.BATTLEFIELD):
        self.controller = controller
        self.character = character
        self.stage = stage
        
    def act(self, gamestate):
        '''Main function called each frame of game loop with updated gamestate.'''
        
        if gamestate.menu_state in (melee.Menu.IN_GAME,
                                    melee.Menu.SUDDEN_DEATH):
            self.play_frame(gamestate)  # rand note, paused wont advance frame
        else:
            self.menu_nav(gamestate)
        
    def menu_nav(self, gamestate):
        '''Processes menus with given character, stage.'''
        melee.MenuHelper.menu_helper_simple(gamestate,
                                            self.controller,
                                            self.character,
                                            self.stage,
                                            '', # connect code
                                            0,  # cpu_level (0 for N/A)
                                            0,  # costume
                                            autostart=True)
    
    def play_frame(self, gamestate):
        '''Bot game logic implemented here.'''
        pass
        
class FalcoBot(Bot):
    
    def __init__(self, controller, debug=False):
        super().__init__(controller=controller,
                         character=melee.Character.FALCO,
                         stage=melee.Stage.FINAL_DESTINATION)
        self.debug = debug
        self.timer = 60
        self.jumped = False
        self.frames_since_jump = 0
        self.toggle = False
        self.last_action = None        
        
    def play_frame(self, gamestate):
        if self.debug:
            self.log_actions(gamestate)
        self.short_hop_laser_strat(gamestate)
#        self.standing_laser_strat()
#        self.taunt_strat()
#        self.ragequit()

            
    def standing_laser_strat(self):
        # works, just unoptomized with overlapping/unused B presses
        if self.timer > 0:
            self.controller.release_all()
            self.timer -= 1
        else:
            self.controller.press_button(enums.Button.BUTTON_B)
            self.timer = random.randint(0, 60)
            
    def short_hop_laser_strat(self, gamestate):
        # works, just unoptomized with some early/late B presses
        if gamestate.player[2].action in (enums.Action.STANDING,
                                          enums.Action.LANDING):
            if not self.jumped:
                self.controller.press_button(enums.Button.BUTTON_Y)
                self.jumped = True
                self.timer = random.randint(6, 22)
                return

        self.controller.release_all()
        self.jumped = False
        self.timer -= 1
        if self.timer == 0:
            self.controller.press_button(enums.Button.BUTTON_B)
            
    def calc_short_hop_frames(self, gamestate):
        # kinda working ~ 30 frames bt jumps?
        # actually that's just for non-fast-fall short hop
        if gamestate.player[2].action in (enums.Action.STANDING,
                                          enums.Action.LANDING):
            if not self.jumped:
                self.controller.press_button(enums.Button.BUTTON_Y)
                self.jumped = True
                print(self.frames_since_jump)
                self.frames_since_jump = 0
                return

        self.controller.release_all()
        self.jumped = False
        self.frames_since_jump += 1
        
    def toggle_debug(self):
        self.debug = not self.debug
        
    def log_actions(self, gamestate):
        # prints action if different than last frame. 
        # no inputs, ie doesn't interfere with strategies.
        curr_action = gamestate.player[2].action
        if not curr_action == self.last_action:
            print(curr_action)
            
        self.last_action = curr_action
#        
#    def log_menustate(self, gamestate):
#        gamestate.menu_state
#        ###
        
    ### fun

    def ragequit(self):
        # doesn't work... just equates to multiple start presses
        # also controller doesn't seem to advance frames in pause,
        # hence time.sleep()
        buttons = (enums.Button.BUTTON_START,
                   enums.Button.BUTTON_L,
                   enums.Button.BUTTON_R,
                   enums.Button.BUTTON_A,
                   enums.Button.BUTTON_START)
        presses = [lambda:self.controller.press_button(button)
                   for button in buttons]
        presses.insert(1, lambda:self.controller.release_all())

        for p in presses:
            p()
            print(self.controller.current)
            time.sleep(0.2)
            
    
    def taunt_strat(self):
        # works perfectly
        if self.toggle:
            self.controller.press_button(enums.Button.BUTTON_D_UP)
        else:
            self.controller.release_all()
        self.toggle = not self.toggle