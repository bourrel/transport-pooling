class Clock():
    def __init__(self):
        self.time = 0
        self.actions = []

    def next(self):
        if self.time >= 1440:
            self.time = -1
        else:
            self.time += 1

        return self.time

    def add_action(self, action, args=None):
        """
            Prepare a future action
        """
        pass