import melee
from melee import enums

class Bot:
    '''Decision maker for controller inputs.'''

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
            self.play_frame(gamestate)
        else:
            self.menu_nav(gamestate)
        
    def menu_nav(self, gamestate):
        '''Works to autostart at given character, stage.'''
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
    
class MyBot(Bot):
    
    def __init__(self, controller):
        super().__init__(controller=controller,
                         character=melee.Character.FALCO)
        self.counter = 0
    
    def play_frame(self, gamestate):
        
        self.move_strategy(gamestate)
        
        dist = gamestate.distance
        
    def move_strategy(self, gamestate):
        self.controller.tilt_analog(enums.Button.BUTTON_MAIN,
                                    0.1, 0.5)
        if self.counter > 0:
            self.controller.press_button(enums.Button.BUTTON_Y)
            self.counter = 0
        else:
            self.controller.release_button(enums.Button.BUTTON_Y)
            self.counter += 1
            
#        self.controller.flush()        
        
    def other_strategy(self, gamestate):
        dist = gamestate.distance
        