from random import choices

import requests

from .city import City
from .vehicle import Vehicle


class Plan():
    def __init__(self, city_names):
        self.city_names = city_names
        self.init_cities()
        self.vehicles = []

    def init_cities(self):
        self.cities = []
        self.total_population = 0

        # Get cities data
        for city in self.city_names:
            resp = requests.get(self._get_nominatim_url(city))
            if resp.status_code == 200:
                json = resp.json()
                for feature in json["features"]:
                    try:
                        # Call population in try/except to check if present in JSON 
                        self.total_population += int(feature["properties"]["extratags"]["population"])
                        self.cities.append(City(feature["properties"], feature["bbox"]))
                        break
                    except KeyError:
                        continue

        # Set cities importance
        for city in self.cities:
            city.update_importance(self.total_population)

    def _get_nominatim_url(self, city:str):
        url = "https://nominatim.openstreetmap.org/search?"
        options = {
            "country": "France",
            "format": "geojson",
            "extratags": "1",
            # "polygon_geojson": "1",
            "city": city
        }
        for idx, (key, val) in enumerate(options.items()):
            if idx != 0:
                url += "&"
            url += key + "=" + val
        return url

    def create_address(self):
        population = range(0, len(self.cities))
        weights = [city.importance for city in self.cities]

        city = self.cities[choices(population, weights)[0]]
        return city.get_random_point()

    def insert_vehicles(self, vehicle_count=10):
        population = range(0, len(self.cities))
        weights = [city.importance for city in self.cities]

        vehicles = []
        for _ in range(vehicle_count):
            city = self.cities[choices(population, weights)[0]]
            vehicles.append(Vehicle.from_city(city))
        return vehicles
