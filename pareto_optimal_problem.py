from citizen import Citizen
import utils
import random
import matplotlib.pyplot as plt


class ParetoOptimalProblem:
    def __init__(self, data):
        self.data = data
        self.length = 1000

    def g_of_x(self, x):
        y = ((x - 2) * (x - 2)) + 10
        return y

    def f_of_x(self, x):
        y = ((x + 2) * (x + 2)) - 10
        return y

    def is_done(self, best):
        return False

    def init_citizen(self):
        citizen = Citizen()
        for i in range(self.length):
            citizen.x[i] = random.randint(-30, 30)
        return citizen

    def calc_fitness(self, population):
        for citizen in population:
            fitness = 0
            for i in range(self.length):
                fitness = fitness + (0.4 * self.f_of_x(citizen.x[i]) + 0.6 * self.g_of_x(citizen.x[i]))
            citizen.fitness = round(fitness / self.length, 5)

    def print_best(self, gav, iter_num):
        print("Iteration number: " + str(iter_num))
        print("Best: ")
        print_vec = ''
        for i in range(self.length):
            print_vec = print_vec + str(round(gav[0].x[i], 3)) + ', '
        print(print_vec)
        print("Fitness: " + str(gav[0].fitness))
        print()
        with open("output.txt", 'a') as file:
            file.write("Best fitness: " + str(gav[0].fitness) + "\n")
            file.write("    Iteration number: " + str(iter_num) + "\n")
            file.write("    Fitness average: " + str(round(utils.average(gav, self.data.ga_popsize), 3)) + "\n")
            file.write("    Fitness deviation: " + str(round(utils.deviation(gav, self.data.ga_popsize), 3)) + "\n")

    def mutate(self, citizen):
        for i in range(self.length):
            number = random.random()
            plus_minus = random.randint(0, 1)
            if plus_minus == 0:
                plus_minus = -1
            citizen.x[i] = citizen.x[i] + (plus_minus * number)

    def crossover(self, first_parent, second_parent):
        citizen = Citizen()
        for i in range(self.length):
            citizen.x[i] = (first_parent.x[i] + second_parent.x[i]) / 2
        return citizen

    def calculate_pareto(self, best_citizen):
        x = best_citizen.x
        x.sort()
        y = []
        for i in range(self.length):
            y.append(0.4 * self.f_of_x(x[i]) + 0.6 * self.g_of_x(x[i]))
        plt.scatter(x, y)
        plt.savefig("pareto.png")
