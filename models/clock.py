class Clock():
    def __init__(self):
        self.time = 0
        self.actions = []
    
    def next(self):
        self.time += 1
        return self.time
    
    def add_action(self, action):
        """
            Prepare a future action
        """
        pass