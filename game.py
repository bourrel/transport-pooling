from models.plan import Plan
from models.clock import Clock


class Game(object):
    def __init_(self, plan):
        self.vehicles = []
        self.orders = []
        self.plan = plan
        self.clock = Clock()

    def _init_vehicles(self):
        self.vehicles = self.plan.insert_vehicles()

    def _cluster_orders(self):
        """
            Try to find orders that can be matched together.

            Orders that can be clustered must have:
                - starting point within a radius of 1 km
                - ending point within a radius of 10 km
        """
        pass

    def _get_available_vehicles(self, order):
        """
            Get a list of all available vehicles sorted by distance with order
        """
        pass

    def _start_ride(self):
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
        pass

    def _new_order(self):
        """
            Add a new order to the game with position X, Y
        """
        pass

    def run(self):
        """
            Run the simulation.

            Simulate a week of transportation.
        """
        pass
