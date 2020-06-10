import random

from models.plan import Plan
from models.clock import Clock
from models.order import Order


class Game():
    def __init__(self, plan):
        self.vehicles = []
        self.orders = []
        self.plan = plan
        self.clock = Clock()
        self._init_vehicles()

    def _init_vehicles(self):
        self.vehicles = self.plan.insert_vehicles()

    def _cluster_orders(self):
        """
            Try to find orders that can be matched together.

            Orders that can be clustered must have:
                - starting point within a radius of 1 km
                - ending point within a radius of 10 km
        """
        return []

    def _get_available_vehicles(self, order):
        """
            Get a list of all available vehicles sorted by distance with order
        """
        return []

    def _start_ride(self, order, vehicles):
        """
            - Time from nearest vehicle to order
                - Compute time from vehicle to further address.
                - Add 2 minutes for each stop
            - Change order status to WAITING
            - Change vehicle status to LOADING_PASSENGERS

            After time from vehicle to order:
            - Change order status to DONE
            - Change vehicle status to DRIVING
            - Compute driving time for vehicle
                - Compute time from current to further address
                - Add 2 minutes for each stop
        """
        return []

    def _new_orders(self):
        """
            Add a new order to the game with position X, Y

            TODO:
        """
        orders = random.randint(0, 10)

        for _ in range(orders):
            start = self.plan.create_address()
            end = self.plan.create_address()
            self.orders.append(Order(start, end))

    def run(self):
        """
            Run the simulation.

            Simulate a week of transportation.
        """
        while self.clock.next() > 0:
            self._new_orders() # Get new orders
            self._cluster_orders() # Try to cluster orders

            for order in self.orders:
                vehicles = self._get_available_vehicles(order)
                self._start_ride(order, vehicles)
            
        print("Done")
