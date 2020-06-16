import csv
import math
import random

import mpu
from tqdm import tqdm

from config.database import cursor, db
from models.clock import Clock
from models.order import Order, OrderStatus
from models.plan import Plan
from models.vehicle import VehicleStatus

MAX_START_RADIUS = 1000 # 1 km
MAX_END_RADIUS = 5000 # 5 km


class Game():
    def __init__(self, plan, out_file):
        self._id = None
        self.vehicles = []
        self.orders = []
        self.plan = plan
        self.clock = Clock()
        out_file = open(out_file, "w")
        self.out_file = csv.writer(out_file)
        self.out_file.writerow([
            "Order count", 
            "Order unavailable",
            "Order waiting",
            "Order in progress",
            "Order done",
            "Vehicle waiting",
            "Vehicle driving",
            "Vehicle loading",
            "Vehicle dropping",
        ])
        self._save_in_database()
        self._init_vehicles()

    def _save_in_database(self):
        cities = ", ".join([str(c) for c in self.plan.cities])
        query = "INSERT INTO game SET cities = \"{}\";".format(cities)
        cursor.execute(query)
        db.commit()
        self._id = cursor.lastrowid

    def _init_vehicles(self):
        self.vehicles = self.plan.insert_vehicles(game_id=self._id)

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

        waiting_orders = [order for order in self.orders if order.status not in [OrderStatus.IN_PROGRESS, OrderStatus.DONE]]
        for idx, order in enumerate(waiting_orders):
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

    def _get_ride_time(self, distance, stops=0):
        """
            Average ride speed is 60km/h or 16,67m/s

            Every stop adds 2 minutes
        """
        ride_time_in_seconds = distance / 16.67
        ride_time = math.ceil(ride_time_in_seconds / 60)
        ride_time += stops * 2
        return ride_time

    def _start_loading(self, order, vehicles):
        """
            - Time from nearest vehicle to order departure
                - Compute time from vehicle to further address.
                - Add 2 minutes for each stop
            - Change order status to WAITING
            - Change vehicle status to LOADING_PASSENGERS
        """
        nearest_vehicle = vehicles[0] # vehicles are already sorted by distance

        distances = []
        for departures in order.begin:
            distances.append(self._get_position_distance(departures, nearest_vehicle.position))

        max_distance = max(distances)
        waiting_time = self._get_ride_time(max_distance, stops=len(order.begin) - 1)

        next_position_idx = [idx for idx, d in enumerate(distances) if d == max_distance][0]
        next_position = order.begin[next_position_idx]

        nearest_vehicle.change_status(VehicleStatus.LOADING_PASSENGERS)
        self.clock.postpone_action(action=self._start_ride, wait=waiting_time, args=[order, nearest_vehicle, next_position])

    def _start_ride(self, order, vehicle, position):
        """
            Once a vehicle has made a ride to departure, load all passengers.

            - Change order status to DONE
            - Change vehicle status to DRIVING
            - Change vehicle position
            - Compute driving time for vehicle
                - Compute time from current to nearest destination address
        """
        order.change_status(OrderStatus.IN_PROGRESS)
        vehicle.change_status(VehicleStatus.DRIVING)
        vehicle.position = position

        distances = []
        for arrivals in order.destinations:
            distances.append(self._get_position_distance(arrivals, vehicle.position))

        min_distance = min(distances)
        waiting_time = self._get_ride_time(min_distance)

        next_position_idx = [idx for idx, d in enumerate(distances) if d == min_distance][0]
        next_position = order.destinations[next_position_idx]

        self.clock.postpone_action(
            action=self._start_drop,
            wait=waiting_time,
            args=[order, vehicle, next_position]
        )

    def _start_drop(self, order, vehicle, position):
        """
            Once the vehicle has made the ride to first dropping zone.

            - Change vehicle status to DROP_PASSENGERS
            - Change vehicle position
            - Compute driving time for vehicle
                - Compute time from current to further address
                - Add 2 minutes for each stop
        """
        vehicle.change_status(VehicleStatus.DROP_PASSENGERS)
        vehicle.position = position

        if len(order.destinations) == 1:
            self._stop_ride(order, vehicle, position)
        else:
            distances = []
            for arrivals in order.destinations:
                distances.append(self._get_position_distance(arrivals, vehicle.position))

            max_distance = max(distances)
            waiting_time = self._get_ride_time(max_distance, stops=len(order.destinations) - 1)

            next_position_idx = [idx for idx, d in enumerate(distances) if d == max_distance][0]
            next_position = order.destinations[next_position_idx]

            self.clock.postpone_action(
                action=self._stop_ride,
                wait=waiting_time,
                args=[order, vehicle, next_position]
            )

    def _stop_ride(self, order, vehicle, position):
        """
            Once the ride is done:
            - Change vehicle status to WAITING
            - Change vehicle position
            - Change order to DONE
        """
        order.change_status(OrderStatus.DONE)
        vehicle.change_status(VehicleStatus.WAITING)
        vehicle.position = position

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
        return new_orders, orders

    def _report(self, order_count):
        order_status = [order.status for order in self.orders]
        vehicle_status = [vehicle.status for vehicle in self.vehicles]

        self.out_file.writerow([
            order_count,
            order_status.count(OrderStatus.UNAVALAIBLE),
            order_status.count(OrderStatus.WAITING),
            order_status.count(OrderStatus.IN_PROGRESS),
            order_status.count(OrderStatus.DONE),
            vehicle_status.count(VehicleStatus.WAITING),
            vehicle_status.count(VehicleStatus.DRIVING),
            vehicle_status.count(VehicleStatus.LOADING_PASSENGERS),
            vehicle_status.count(VehicleStatus.DROP_PASSENGERS),
        ])
        return 0

    def run(self):
        """
            Run the simulation.

            Simulate a week of transportation.
        """
        order_count = 0

        progress_bar = tqdm(self.clock.max + 1)
        while self.clock.next():
            self._report(order_count)
            new_orders, order_count = self._new_orders() # Get new orders
            self._cluster_or_insert_orders(new_orders) # Try to cluster orders

            for order in self.orders:
                vehicles = self._get_nearest_vehicles(order)
                if len(vehicles) > 0:
                    self._start_loading(order, vehicles)
            progress_bar.update(1)
        print("Done")
