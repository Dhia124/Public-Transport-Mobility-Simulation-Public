import random
import time
import pygame
from pygame.locals import QUIT

class City:
    def __init__(self, size):
        self.size = size
        self.roads = [[random.choice([True, False]) for _ in range(size)] for _ in range(size)]
        self.bus_stops = [(random.randint(0, size - 1), random.randint(0, size - 1)) for _ in range(40)]
        self.blocked_streets = set()

class PublicTransportVehicle:
    def __init__(self, vehicle_id, route, position, blocked_streets):
        self.vehicle_id = vehicle_id
        self.route = route
        self.next_stop = 0
        self.position = position
        self.blocked_streets = blocked_streets
        self.passengers = []
        self.status = "waiting"

    def move(self, city, num_positions_to_move):
        for _ in range(num_positions_to_move):
            if self.position != self.route[self.next_stop]:
                self.move_towards_destination(city)
            else:
                self.handle_stop_arrival(city)
                break

    def move_towards_destination(self, city):
        delta_x = self.route[self.next_stop][0] - self.position[0]
        delta_y = self.route[self.next_stop][1] - self.position[1]

        new_x, new_y = self.position[0], self.position[1]
        if delta_x != 0:
            new_x += delta_x // abs(delta_x)
        elif delta_y != 0:
            new_y += delta_y // abs(delta_y)

        new_position = (new_x, new_y)
        if self.is_valid_move(city, new_position):
            self.position = new_position
        else:
            self.handle_alternative_route(city)

    def is_valid_move(self, city, new_position):
        return 0 <= new_position[0] < city.size and 0 <= new_position[1] < city.size and new_position not in self.blocked_streets

    def handle_alternative_route(self, city):
        alternative_positions = [(x, y) for x in range(self.position[0] - 1, self.position[0] + 2)
                                 for y in range(self.position[1] - 1, self.position[1] + 2)
                                 if 0 <= x < city.size and 0 <= y < city.size and (x, y) not in self.blocked_streets ]
        if alternative_positions:
            self.position = random.choice(alternative_positions)
        else:
            print(f"Vehicle {self.vehicle_id}: No alternative routes available. Staying in the current position.")

    def handle_stop_arrival(self, city):
        self.next_stop = (self.next_stop + 1) % len(self.route)
        print(f"Vehicle {self.vehicle_id} has arrived at stop {self.next_stop}.")
        if self.next_stop == 0:
            self.complete_route()

    def complete_route(self):
        print(f"Vehicle {self.vehicle_id} has completed its route.")
        self.status = "waiting"

class Passenger:
    def __init__(self, passenger_id, origin, destination, blocked_streets):
        self.passenger_id = passenger_id
        self.destination = destination
        self.position = origin
        self.blocked_streets = blocked_streets
        self.BusTaken = False
        self.BusStartPosition = (-1, -1)
        self.Bus = None
        self.foot_steps = 0
        self.vehicle_steps = 0

    def move(self, city, vehicles, take_public_transport_probability=0.5):
        if self.position == self.destination:
            return   # Passenger has reached the destination, no need to move further

        current_x, current_y = self.position
        dest_x, dest_y = self.destination

        if self.BusTaken:
            self.vehicle_steps += 1
            return

        # Check if the passenger is on a bus stop
        if self.position in city.bus_stops:
            matching_vehicles = [vehicle for vehicle in vehicles if (self.position == vehicle.position)]
            if matching_vehicles:
                vehicle = random.choice(matching_vehicles)
                self.BusTaken = True
                self.Bus = vehicle
                self.vehicle_steps += 1
                return  # Skip the walking part if taking public transport

        # Calculate the direction towards the destination
        delta_x = dest_x - current_x
        delta_y = dest_y - current_y

        self.foot_steps += 1

        # Move towards the destination or find an alternative route
        new_x, new_y = current_x, current_y
        if delta_x != 0:
            new_x += delta_x // abs(delta_x)
        elif delta_y != 0:
            new_y += delta_y // abs(delta_y)

        # Check if the new position is within the city grid and accessible if not find alternative
        if 0 <= new_x < city.size and 0 <= new_y < city.size and (new_x, new_y) not in self.blocked_streets:
            self.position = (new_x, new_y)
        else:
            alternative_positions = [(x, y) for x in range(current_x - 1, current_x + 2)
                                     for y in range(current_y - 1, current_y + 2)
                                     if 0 <= x < city.size and 0 <= y < city.size and (x, y) not in self.blocked_streets]
            if alternative_positions:
                self.position = random.choice(alternative_positions)

def run_simulation(city, vehicles, passengers, num_steps):
    simulation = Simulation(city, vehicles, passengers)
    simulation.run(num_steps)

class Simulation:
     def __init__(self, city, vehicles, passengers):
        self.city = city
        self.vehicles = vehicles
        self.passengers = passengers

     def run(self, num_steps):

        for step in range(num_steps):
            print(f"--- Step {step + 1} ---")

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    return

     # Move public transport vehicles
            for vehicle in self.vehicles:
                num_positions_to_move = random.randint(1, 4)
                vehicle.move(self.city, num_positions_to_move)
                print(f"Vehicle {vehicle.vehicle_id} Position: {vehicle.position}")
                for passenger in vehicle.passengers:
                    passenger.position = vehicle.position
                    for p in self.passengers:
                        if p == passenger:
                            p.position = passenger.position
                    if passenger.position == passenger.destination:
                        vehicle.passengers.remove(passenger)

         # Move passengers
            for passenger in self.passengers:
                print(passenger.destination)
                print(passenger.position)
                passenger.move(self.city, self.vehicles)
                print(f"Passenger {passenger.passenger_id} Position: {passenger.position}")
                if not passenger.BusTaken and passenger.position in self.city.bus_stops:
                    # Find available buses at the bus stop
                    available_buses = [vehicle for vehicle in self.vehicles if vehicle.position == passenger.position and vehicle.status == "waiting"]
                    if available_buses:
                        # Choose a random available bus
                        chosen_bus = random.choice(available_buses)
                        # Board the bus
                        chosen_bus.passengers.append(passenger)
                        passenger.Bus = chosen_bus
                        passenger.BusStartPosition = passenger.position
                        passenger.BusTaken = True
                        print(f"Passenger {passenger.passenger_id} boarded Vehicle {chosen_bus.vehicle_id}.")

        # Draw the city, vehicles, and passengers
            screen.fill((255, 255, 255))  # White background

            # Draw roads
            for y, row in enumerate(self.city.roads):
                for x, road in enumerate(row):
                    color = (0, 0, 0) if road else (255, 255, 255)
                    
                    pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

            # Draw bus stops
            for stop in self.city.bus_stops:
                pygame.draw.circle(screen, (0, 0, 255), (stop[0] * CELL_SIZE + CELL_SIZE // 2, stop[1] * CELL_SIZE + CELL_SIZE // 2), 10)

            # Draw blocked_streets
            for block in self.city.blocked_streets:
                pygame.draw.rect(screen, (180, 180, 180), (block[0] * CELL_SIZE, block[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))



            # Draw vehicles
            for vehicle in self.vehicles:
                pygame.draw.rect(screen, (255, 0, 0), (vehicle.position[0] * CELL_SIZE, vehicle.position[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))

            # Draw passengers
            for passenger in self.passengers:
                pygame.draw.circle(screen, (0, 255, 0), (passenger.position[0] * CELL_SIZE + CELL_SIZE // 2, passenger.position[1] * CELL_SIZE + CELL_SIZE // 2), 5)

            pygame.display.flip()
            clock.tick(1)    # Limit frames per second

     pygame.quit() 

# Constants
CELL_SIZE = 100
SCREEN_SIZE = (1000, 800)
pygame.init()
screen_size = (1000, 800)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption("City Simulation")

clock = pygame.time.Clock()
# Create a city, vehicles, and passengers
city_size = 10
city = City(size=city_size)
start_stop = random.choice(city.bus_stops)
timetable = random.sample(city.bus_stops, len(city.bus_stops))
timetable1 = random.sample(city.bus_stops, len(city.bus_stops))



blocked_streets = (random.randint(0, city_size - 1), random.randint(0, city_size - 1))
blocked_streets2 = (random.randint(0, city_size - 1), random.randint(0, city_size - 1))
blocked_streets3 = (random.randint(0, city_size - 1), random.randint(0, city_size - 1))
blocked_streets4 = (random.randint(0, city_size - 1), random.randint(0, city_size - 1))
blocked_streets5 = (random.randint(0, city_size - 1), random.randint(0, city_size - 1))




print(blocked_streets)
city.blocked_streets.add(blocked_streets)
city.blocked_streets.add(blocked_streets2)
city.blocked_streets.add(blocked_streets3)
city.blocked_streets.add(blocked_streets4)
city.blocked_streets.add(blocked_streets5)


vehicles = []
start_stop = (2, 4)
vehicle = PublicTransportVehicle(vehicle_id=1, route=timetable, position=start_stop, blocked_streets=city.blocked_streets)
vehicle2 = PublicTransportVehicle(vehicle_id=2, route=timetable1, position=start_stop, blocked_streets=city.blocked_streets)
print(city.blocked_streets)
vehicles.append(vehicle)
vehicles.append(vehicle2)

passenger1 = Passenger(passenger_id=1, origin=(1, 1), destination=(6, 6), blocked_streets=city.blocked_streets)
passenger2 = Passenger(passenger_id=2, origin=(2, 2), destination=(5, 5), blocked_streets=city.blocked_streets)

# Run the simulation
run_simulation(city, vehicles, [passenger1, passenger2], num_steps=20)
