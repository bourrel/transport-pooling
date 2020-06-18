from typing import Tuple
from math import radians


class Position():
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

    def as_radians(self):
        return [radians(self.latitude), radians(self.longitude)]

    def as_tuple(self):
        return (self.latitude, self.longitude)
