from enum import Enum

from .position import Position
from config.database import cursor, db


class OrderStatus(Enum):
    UNAVALAIBLE = "UNAVALAIBLE"
    WAITING = "WAITING"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


class Order():
    """
        Order represent a client ride.

        It can contain one or more rides.
    """

    def __init__(self, start: Position, end: Position, game_id=None):
        self._id = None
        self.begin = [start]
        self.destinations = [end]
        self.status = OrderStatus.UNAVALAIBLE
        self.game_id = game_id
        self.full = False

    def save_in_database(self):
        if self.game_id != None:
            query = "INSERT INTO adenoa.order SET status = \"{}\", departures = 1, arrivals = 1, game_id = {};".format(str(self.status), self.game_id)
            cursor.execute(query)
            db.commit()
            self._id = cursor.lastrowid

    def change_status(self, status):
        self.status = status

    def insert_order(self, new_order):
        """
            Add new ride to the order.
        """
        self.begin.extend(new_order.begin)
        self.destinations.extend(new_order.destinations)

        if len(self.begin) >= 25:
            self.full == True

        if self.game_id:
            query = """
                UPDATE adenoa.order SET
                    departures = {},
                    arrivals = {},
                    full = {}
                WHERE id = {};
            """.format(len(self.begin), len(self.destinations), int(self.full), self._id)
            cursor.execute(query)
            db.commit()

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
