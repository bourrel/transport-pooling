from enum import Enum

from position import Position

class OrderStatus(Enum):
    UNAVALAIBLE = 1
    WAITING = 2
    DONE = 3


class Order():
    """
        Order represent a client ride.

        It can contain one or more rides.
    """

    def __init__(self, start: Position, end: Position):
        self.begin = [start]
        self.destinations = [end]
        self.status = OrderStatus.UNAVALAIBLE

    def is_near(self, start: Position, end: Position):
        """
            Check if a new ride can be added to this order
        """
        pass

    def insert_order(self, start: Position, end: Position):
        """
            Add new ride to the order.
        """
        pass
