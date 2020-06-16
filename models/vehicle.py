from enum import Enum

from config.database import cursor, db


class VehicleStatus(Enum):
    WAITING = 1
    DRIVING = 2
    LOADING_PASSENGERS = 3
    DROP_PASSENGERS = 4


class Vehicle():
    def __init__(self, start_position, capacity=10, game_id=None):
        self._id = None
        self.status = VehicleStatus.WAITING
        self.position = start_position
        self.capacity = capacity

        if game_id != None:
            query = "INSERT INTO vehicle SET capacity = \"{}\", game_id = \"{}\";".format(capacity, game_id)
            cursor.execute(query)
            db.commit()
            self._id = cursor.lastrowid

    @classmethod
    def from_city(cls, city, game_id=None):
        return cls(city.get_random_point(), game_id=game_id)

    def change_status(self, status):
        self.status = status