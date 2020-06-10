from .position import Position
from random import uniform


class City():
    def __init__(self, properties, bbox):
        self.name = properties["display_name"].split(",")[0]
        self.place_id = properties["place_id"]
        self.wikidata = properties["extratags"]["wikidata"]
        self.wikipedia = properties["extratags"]["wikipedia"]
        self.population = int(properties["extratags"]["population"])
        self.bbox = bbox
        self.importance = 0

    def update_importance(self, total_population):
        self.importance = self.population / total_population

    def get_random_point(self):
        """
            Return a point in the bounding box area of the city.

            TODO:
                Replace bounding box with the polygon of the city.
                Then, generate random uniform point in the space.
                (Divide polygon in triangles - random point in triangle weighted by area)
        """
        x = uniform(self.bbox[1], self.bbox[3])
        y = uniform(self.bbox[0], self.bbox[2])
        return Position(x, y)