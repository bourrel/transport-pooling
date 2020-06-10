from models.plan import Plan
from game import Game


if __name__ == "__main__":
    plan = Plan(["Dreux", "Vernouillet"])
    # Print city informations
    print("Population : ", plan.total_population)
    for city in plan.cities:
        print(city.name, ":", city.importance, ",", city.population)

    vehicles = plan.insert_vehicles()

    game = Game()
    game.run()
