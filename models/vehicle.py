from enum import Enum


class VehicleStatus(Enum):
    WAITING = 1
    DRIVING = 2
    LOADING_PASSENGERS = 3
    DROP_PASSENGERS = 4


class Vehicle():
    def __init__(self, start_position, capacity=10):
        self.status = VehicleStatus.WAITING
        self.position = start_position
        self.capacity = capacity

    @classmethod
    def from_city(cls, city):
        return cls(city.get_random_point())
