import argparse

from models.plan import Plan
from game import Game

parser = argparse.ArgumentParser()
parser.add_argument('--cities', nargs='+', type=str, help='List of cities splitted by "," to add to plan')
parser.add_argument('--file', type=str, help='List of cities splitted by "," to add to plan')
parser.add_argument('out_file', type=str, help='CSV output')
args = parser.parse_args()


if __name__ == "__main__":
    plan = None
    if args.file != None:
        cities_file = open(args.file)
        cities = cities_file.readlines().replace("\n", "").replace(" ", "")
        plan = Plan(cities.split(","))
    elif len(args.cities) > 0:
        plan = Plan(args.cities)
    else:
        exit(0)

    # Print city informations
    print("Population : ", plan.total_population)
    for city in plan.cities:
        print(city.name, ":", city.importance, ",", city.population)

    vehicles = plan.insert_vehicles()

    game = Game(plan, args.out_file)
    game.run()
