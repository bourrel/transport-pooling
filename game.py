import random

import mpu

from models.vehicle import VehicleStatus
from models.clock import Clock
from models.order import Order, OrderStatus
from models.plan import Plan

MAX_START_RADIUS = 1000 # 1 km
MAX_END_RADIUS = 5000 # 5 km


class Game():
    def __init__(self, plan):
        self.vehicles = []
        self.orders = []
        self.plan = plan
        self.clock = Clock()
        self._init_vehicles()

    def _init_vehicles(self):
        self.vehicles = self.plan.insert_vehicles()

    def _get_position_distance(self, first_pos, second_pos):
        """
            Get distance between two points on earth
        """
        dist = mpu.haversine_distance((first_pos.as_tuple()), (second_pos.as_tuple()))
        return dist * 1000

    def _can_be_clustered(self, first_order, second_order):
        """
            Check if pair of orders can be clustered together
        """
        first_begin_pos = first_order.get_begin_centroid()
        second_begin_pos = second_order.get_begin_centroid()

        distance_begin = self._get_position_distance(first_begin_pos, second_begin_pos)
        if distance_begin > MAX_START_RADIUS:
            return False, -1, -1

        first_destination_pos = first_order.get_destination_centroid()
        second_destination_pos = second_order.get_destination_centroid()

        distance_end = self._get_position_distance(first_destination_pos, second_destination_pos)
        if distance_end >= MAX_START_RADIUS:
            return False, -1, -1

        return True, distance_begin, distance_end

    def _get_new_order_possible_clusters(self, new_order):
        possible_clusters = []

        for idx, order in enumerate(self.orders):
            can_be_clustered, distance_begin, distance_end = self._can_be_clustered(order, new_order)
            if can_be_clustered:
                possible_clusters.append((idx, distance_begin, distance_end))
        return possible_clusters

    def _cluster_or_insert_orders(self, new_orders):
        """
            Try to find orders that can be matched together.

            Orders that can be clustered must have:
                - starting point within a radius of 1 km
                - ending point within a radius of 10 km
            Otherwise, insert them as new orders
        """
        for new_order in new_orders:
            possible_clusters = self._get_new_order_possible_clusters(new_order)

            if len(possible_clusters) > 0:
                cluster_idx = sorted(possible_clusters, key=lambda x: x[1])[0]
                self.orders[cluster_idx[0]].insert_order(new_order)
            else:
                self.orders.append(new_order)

    def _get_nearest_vehicles(self, order):
        """
            Get a list of all available vehicles sorted by distance with order
        """
        vehicle_list = []
        for idx, vehicle in enumerate(self.vehicles):
            if vehicle.status == VehicleStatus.WAITING or vehicle.status == VehicleStatus.LOADING_PASSENGERS:
                distance = self._get_position_distance(vehicle.position, order.get_begin_centroid())
                vehicle_list.append((idx, distance))

        nearest_vehicles = sorted(vehicle_list, key=lambda vh: vh[1])[:10]
        return [self.vehicles[vh_idx] for vh_idx, _ in nearest_vehicles]

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
                Generate orders following a multi-variate distribution which will peak at:
                - 8h30
                - 13h
                - 18h
        """
        orders = random.randint(0, 10)

        new_orders = []
        for _ in range(orders):
            start = self.plan.create_address()
            end = self.plan.create_address()
            order = Order(start, end)
            new_orders.append(order)
            self.clock.postpone_action(action=order.change_status, wait=2, args=[OrderStatus.WAITING])
        return new_orders

    def run(self):
        """
            Run the simulation.

            Simulate a week of transportation.
        """
        while self.clock.next() > 0:
            new_orders = self._new_orders() # Get new orders
            self._cluster_or_insert_orders(new_orders) # Try to cluster orders

            for order in self.orders:
                vehicles = self._get_nearest_vehicles(order)

                self._start_ride(order, vehicles)

        print("Done")
