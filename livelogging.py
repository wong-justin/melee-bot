import threading

class LiveInputsThread(threading.Thread):
    '''Awaits user input during a game to obtain live information.
    Used for live debugging or poking around; nothing saved (as opposed to melee.logger).
    Mainly gets stats from melee.gamestate attrs.
    See on_input() for available commands.'''
    
    def __init__(self, console=None, onshutdown=None):
        self.console = console          # needed for processing times
        self.onshutdown = onshutdown    # callback
        self.max_processing = 0
        super().__init__(name='input-thread')
        self.start()
        
    def run(self):
        '''Callback whenever user inputs, either to show stat or stop everything.'''
        while True:
            _input = input()
            if _input in ('quit', 'kill', 'stop'):
                break
                
            self.on_input(_input)
                
        self.onshutdown()
            
    def on_input(self, stat):
        '''Prints desired game stat, either from last frame or cumulative stat.'''

        stats = {
            't': ('Max bot processing time:', 
                  '{:.2f}'.format(self.max_processing), 
                  'ms for a frame'),
            'f': ('Frame num:', 
                  self.gamestate.frame),
            'p': ('Percents:', 
                  '{}%  {}%'.format(self.gamestate.player[1].percent,   # hard to replicate KeyError
                                    self.gamestate.player[2].percent)), # gamestate.player[numpy int]
            'd': ('Distance:', 
                  self.gamestate.distance)
        }
        # '[command] -c': print continuously until next input?
        if stat in stats:
            print( *stats[stat] )
            
    def update(self, gamestate):
        '''Called each frame to update recent stats.'''
        self.max_processing = max(self.max_processing, self.console.processingtime)
        self.gamestate = gamestate
        