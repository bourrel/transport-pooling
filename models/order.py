from uuid import uuid4
from enum import Enum

from .position import Position


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
        self._id = uuid4()
        self.begin = [start]
        self.destinations = [end]
        self.status = OrderStatus.UNAVALAIBLE

    def insert_order(self, new_order):
        """
            Add new ride to the order.
        """
        self.begin.extend(new_order.begin)
        self.destinations.extend(new_order.destinations)

    def get_begin_centroid(self):
        if len(self.begin) == 1:
            return self.begin[0]

        centroid_x = 0
        centroid_y = 0
        for position in self.begin:
            centroid_x += position.latitude
            centroid_y += position.longitude
        return Position((centroid_x / len(self.begin)), (centroid_y / len(self.begin)))

    def get_destination_centroid(self):
        if len(self.destinations) == 1:
            return self.destinations[0]

        centroid_x = 0
        centroid_y = 0
        for position in self.destinations:
            centroid_x += position.latitude
            centroid_y += position.longitude
        return Position((centroid_x / len(self.destinations)), (centroid_y / len(self.destinations)))
