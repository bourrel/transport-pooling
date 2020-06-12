
class Action():
    def __init__(self, action, datetime, args):
        self.action = action
        self.datetime = datetime
        self.args = args

    def run(self):
        self.action(*self.args)


class Clock():
    def __init__(self):
        self.time = 0
        self.action_queue = []

    def next(self):
        if self.time >= 1440:
            self.time = -1
        else:
            self.time += 1

        self._execute_queue()
        return self.time

    def _execute_queue(self):
        temp_queu = self.action_queue
        self.action_queue = []

        for action in temp_queu:
            if action.datetime == self.time:
                action.run()
            else:
                self.action_queue.append(action)

    def postpone_action(self, action, wait, args=None):
        """
            Prepare a future action
        """
        action = Action(action, self.time + wait, args)
        self.action_queue.append(action)