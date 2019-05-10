import math


class Citizen:
    def __init__(self, str='', fitness=0, age=0, cap=0):
        self.str = str
        self.board = []
        self.knapsack = []
        self.capacity = cap
        self.fitness = fitness
        self.age = age
        self.penalty_given = False
        self.x = []
        for i in range(1000):
            self.x.append(math.inf)

    def __lt__(self, other):
        return self.fitness < other.fitness
