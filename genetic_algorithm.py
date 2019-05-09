import time
import random
from utils import deviation
from genetic_problem import GeneticProblem
from string_search_problem import StringSearchProblem
from nqueens_problem import NQueensProblem
from knapsack_problem import KnapsackProblem
from baldwin_effect_problem import BaldwinEffectProblem
from nqueens_crossover import NQueensCrossover
from nqueens_mutation import NQueensMutation
from string_search_crossover import StringSearchCrossOver
from string_search_fitness import StringSearchFitness
from combat_early_convergence import CombatEarlyConvergence
from local_optima_signal import LocalOptimaSignal
from selection import Selection
from citizen import Citizen


class GeneticAlgorithm:
    def __init__(self, data):
        self.data = data
        self.local_optima_signals = []
        if self.data.selection == Selection.RANDOM:
            selection = "Randomly choosing from top half selection"
        elif self.data.selection == Selection.RWS:
            selection = "Roulette wheel selection"
        elif self.data.selection == Selection.AGING:
            selection = "Aging selection"
        else:
            selection = "Tournament selection"

        print("Running a genetic algorithm")
        if self.data.genetic_problem == GeneticProblem.STRING_SEARCH:
            self.problem = StringSearchProblem(data)
            if self.data.string_search_fitness == StringSearchFitness.DISTANCE:
                fitness = "ASCII distance from target string fitness function"
            else:
                fitness = "Bulls and cows fitness function"
            if self.data.string_search_crossover == StringSearchCrossOver.ONE_POINT:
                crossover = "One-point crossover"
            else:
                crossover = "Two-point crossover"
            print("Solving the string search problem")
            print("Using:")
            print("    Selection method: " + selection)
            print("    Fitness method: " + fitness)
            print("    Crossover method: " + crossover)
        elif self.data.genetic_problem == GeneticProblem.NQUEENS:
            self.problem = NQueensProblem(data)
            if self.data.queens_crossover == NQueensCrossover.PMX:
                crossover = "PMX crossover"
            else:
                crossover = "OX crossover"
            if self.data.queens_mutation == NQueensMutation.EXCHANGE:
                mutation = "Exchange mutation"
            else:
                mutation = "Simple inversion mutation"
            print("Solving the N-queens problem")
            print("Using:")
            print("    Selection method: " + selection)
            print("    Crossover method: " + crossover)
            print("    Mutation method: " + mutation)
            print("    N is set to: " + str(self.data.queens_num))
        elif self.data.genetic_problem == GeneticProblem.KNAPSACK:
            self.problem = KnapsackProblem(data)
            print("Solving the knapsack problem")
            print("Using:")
            print("    Selection method: " + selection)
            print("    Solving problem number: " + str(self.data.knapsack_problem))
        else:
            self.data.ga_maxiter = 50
            self.data.ga_popsize = 1000
            self.problem = BaldwinEffectProblem(self.data)
            print("Solving the Baldwin effect problem")

    # The actual algorithm run
    def run(self):
        overall_time = time.clock()
        population = []
        buffer = []
        self.init_population(population, buffer)
        iter_num = 0
        for i in range(self.data.ga_maxiter):
            iter_num = i
            start_time = time.clock()
            self.problem.calc_fitness(population)
            population.sort()
            if self.data.genetic_problem == GeneticProblem.BALDWIN:
                population.reverse()
            self.problem.print_best(population, i)
            if self.problem.is_done(population[0]):
                self.print_data(start_time)
                break
            self.handle_local_optima(population)
            self.mate(population, buffer)
            buffer, population = population, buffer
            self.print_data(start_time)

        overall_time = time.clock() - overall_time
        overall_clock_ticks = overall_time * self.data.clocks_per_second
        with open("output.txt", 'a') as file:
            file.write("Overall clock ticks: " + str(overall_clock_ticks) + "\n")
            file.write("Overall time: " + str(overall_time) + "\n")
            file.write("Overall iterations: " + str(iter_num) + "\n")

    # Initialize the population
    def init_population(self, population, buffer):
        for i in range(self.data.ga_popsize):
            population.append(self.problem.init_citizen())
        for i in range(self.data.ga_popsize):
            buffer.append(Citizen())

    # Print the data from the best fitness citizen
    def print_data(self, start_time):
        run_time = time.clock() - start_time
        clock_ticks = run_time * self.data.clocks_per_second
        with open("output.txt", 'a') as file:
            file.write("    Clock ticks elapsed: " + str(round(clock_ticks, 3)) + "\n")
            file.write("    Time elapsed: " + str(round(run_time, 3)) + "\n")
        with open("data", 'a') as file:
            for optima_list in self.local_optima_signals:
                print_str = ""
                for entry in optima_list:
                    print_str = print_str + " " + str(entry)
                file.write(print_str + "\n")
            file.write("Next run\n")
        with open("similarity", 'a') as file:
            for optima_list in self.local_optima_signals:
                print_str = ""
                for entry in optima_list:
                    print_str = print_str + " " + str(entry)
                file.write(print_str + "\n")
            file.write("Next run\n")

    # Mate the citizens to create a new generation
    def mate(self, population, buffer):
        esize = int(self.data.ga_popsize * self.data.ga_elitrate)
        self.elitism(population, buffer, esize)
        # Since aging uses the regular RANDOM from top half selection until we reach a point where we have aged citizens
        # we had to initialize another selection field called original_selection and use it when necessary
        if self.data.original_selection == Selection.AGING:
            self.initialize_aging_data(population)
        for i in range(esize, self.data.ga_popsize):
            i1, i2 = self.select_parents(population)
            blacklisted = True
            while blacklisted:
                buffer[i] = self.problem.crossover(population[i1], population[i2])
                if random.randint(0, 32767) < self.data.ga_mutation:
                    self.problem.mutate(buffer[i])
                blacklisted = self.check_if_blacklisted(buffer[i])
                if random.randint(0, 32767) < 32767 * 0.1:
                    blacklisted = False

    def check_if_blacklisted(self, citizen):
        if self.data.genetic_problem == GeneticProblem.STRING_SEARCH:
            return citizen.str in self.data.blacklist
        elif self.data.genetic_problem == GeneticProblem.NQUEENS:
            return citizen.board in self.data.blacklist
        elif self.data.genetic_problem == GeneticProblem.KNAPSACK:
            return citizen.knapsack in self.data.blacklist
        else:
            return False

    # Move the percentage of elite to the next generation without changing them
    def elitism(self, population, buffer, esize):
        for i in range(esize):
            buffer[i].str = population[i].str
            buffer[i].fitness = population[i].fitness
            buffer[i].board = population[i].board
            buffer[i].knapsack = population[i].knapsack
            buffer[i].capacity = population[i].capacity
            buffer[i].age = population[i].age + 1
        self.data.ga_elitrate = 0.1
        return esize

    # When using aging, upon each generation, find which citizens are older than the GA_age
    def initialize_aging_data(self, population):
        self.data.aged_citizens.clear()
        self.data.chosen_pairs.clear()
        self.data.selection = Selection.AGING
        for i, citizen in enumerate(population):
            if citizen.age > self.data.ga_age:
                self.data.aged_citizens.append(i)

    # Select the parents entries
    def select_parents(self, population):
        if self.data.original_selection == Selection.AGING and self.data.selection == Selection.AGING:
            if len(self.data.aged_citizens) < 2:
                self.data.selection = Selection.RANDOM
                return self.select_parents(population)
            else:
                for i in range(5):
                    i1 = random.choice(self.data.aged_citizens)
                    i2 = random.choice(self.data.aged_citizens)
                    if i2 > i1:
                        i1, i2 = i2, i1
                    if (i1, i2) not in self.data.chosen_pairs:
                        self.data.chosen_pairs.append((i1, i2))
                        return i1, i2
                self.data.selection = Selection.RANDOM
                return self.select_parents(population)
        elif self.data.selection == Selection.RANDOM:
            if self.data.original_selection == Selection.AGING:
                self.data.selection = Selection.AGING
            i1, i2 = self.random_selection()
            return i1, i2
        elif self.data.selection == Selection.RWS:
            weights = []
            if self.data.genetic_problem == GeneticProblem.BALDWIN:
                for citizen in population:
                    weights.append(citizen.fitness)
            else:
                max_weight = population[self.data.ga_popsize - 1].fitness
                for citizen in population:
                    weights.append(max_weight - citizen.fitness)

            overall_weights = sum(weights)
            i1 = self.rws_selection(weights, overall_weights)
            i2 = self.rws_selection(weights, overall_weights)
            return i1, i2
        elif self.data.selection == Selection.TOURNAMENT:
            i1 = self.tournament_selection(population)
            i2 = self.tournament_selection(population)
            return i1, i2
        return 0, 1

    # Random selection from better half of population
    def random_selection(self):
        if self.data.performed_niching:
            esize = int(self.data.ga_popsize * self.data.ga_elitrate)
            i1 = int(random.randint(0, 32767) % esize)
            i2 = int(random.randint(0, 32767) % esize)
        else:
            i1 = int(random.randint(0, 32767) % (self.data.ga_popsize / 2))
            i2 = int(random.randint(0, 32767) % (self.data.ga_popsize / 2))
        return i1, i2

    # Roulette selection, given weights for each citizen's fitness
    def rws_selection(self, weights, overall_weights):
        f = random.randint(0, int(overall_weights))
        for i, weight in enumerate(weights):
            f = f - weight
            if f <= 0:
                return i
        return 0

    # Tournament selection, choosing k citizens and returning the one with the best fitness
    def tournament_selection(self, population):
        best = 0
        for i in range(self.data.ga_k):
            if self.data.performed_niching:
                esize = int(self.data.ga_popsize * self.data.ga_elitrate)
                entry = int(random.randint(0, 32767) % esize)
            else:
                entry = int(random.randint(0, 32767) % self.data.ga_popsize)
            if i == 0 or population[entry].fitness < population[best].fitness:
                best = entry
        return best

    # Check if we're stuck in a local minima and handle it
    def handle_local_optima(self, population):
        self.data.performed_niching = False
        if self.data.local_optima_signal == LocalOptimaSignal.Off:
            return
        if self.data.local_optima_signal == LocalOptimaSignal.Deviation:
            self.deviation_local_optima(population)
        else:
            self.similarity_local_optima(population)
        if self.data.mutation_increased:
            self.data.increased_iteration = self.data.increased_iteration + 1
            if self.data.increased_iteration == 10:
                self.data.ga_mutation = 32767 * self.data.ga_mutationrate
                self.data.mutation_increased = False
            return
        self.check_local_optima_signal(population)

    def deviation_local_optima(self, population):
        window = self.data.ga_popsize / self.data.local_optima_groups_num
        deviation_list = []
        for iteration in range(self.data.local_optima_groups_num):
            start = int(iteration * window)
            end = int((iteration + 1) * window)
            deviation_list.append(round(deviation(population[start:end], int(window)), 3))
        self.local_optima_signals.append(deviation_list)

    def similarity_local_optima(self, population):
        window = self.data.ga_popsize / self.data.local_optima_groups_num
        similarity_list = []
        for iteration in range(8):
            start = int(iteration * window)
            end = int((iteration + 1) * window)
            combinations = 0
            similarity = 0
            for i, citizen_1 in enumerate(population[start:end]):
                if i + 1 > window:
                    break
                for citizen_2 in population[start + i + 1:end]:
                    combinations = combinations + 1
                    similarity = similarity + self.problem.calc_similarity(citizen_1, citizen_2)
            similarity_list.append(round(similarity / combinations, 3))
        self.local_optima_signals.append(similarity_list)

    def check_local_optima_signal(self, population):
        if len(self.local_optima_signals) < 5:
            return
        if self.data.local_optima_signal == LocalOptimaSignal.Deviation:
            zero_counter = 0
            for i, entry in enumerate(self.local_optima_signals[-1]):
                if entry == 0 and i <= self.data.local_optima_groups_num / 2:
                    zero_counter = zero_counter + 1
            if zero_counter / self.data.local_optima_groups_num <= 0.45 or self.local_optima_signals[-1][0] != 0:
                return
        else:
            if self.local_optima_signals[-1][0] >= 0.02:
                return
        self.evade_local_optima(population)

    def evade_local_optima(self, population):
        if self.data.evade_local_optima_method == CombatEarlyConvergence.HYPER_MUTATIONS:
            self.perform_hyper_mutation()
        elif self.data.evade_local_optima_method == CombatEarlyConvergence.NICHING:
            self.perform_niching(population)
        else:
            self.perform_random_immigrants(population)

    def perform_hyper_mutation(self):
        self.data.ga_mutation = 32767
        self.data.mutation_increased = True
        self.data.increased_iteration = 0
        print("Hyper mutation performed")

    def perform_niching(self, population):
        self.data.performed_niching = True
        self.blacklist(population[0])
        self.calc_niching_fitness(population)
        with open("data_before", 'a') as file:
            file.write("Turn\n")
            for cit in population:
                file.write(cit.str + " " + str(cit.fitness) + "\n")
        population.sort()
        with open("data_after", 'a') as file:
            file.write("Turn\n")
            for cit in population:
                file.write(cit.str + " " + str(cit.fitness) + "\n")
        print("Niching performed")

    def perform_random_immigrants(self, population):
        for i in range(self.data.ga_popsize):
            if self.are_similar(population[0], population[i]):
                number = random.randint(0, 9)
                if number != 0:
                    population[i] = self.problem.init_citizen()
        self.problem.calc_fitness(population)
        population.sort()
        print("Random immigrants performed")

    def calc_niching_fitness(self, population):
        max_fitness = -1
        for i in range(self.data.ga_popsize):
            population[i].fitness = population[i].fitness / self.calc_shared_fitness(population, population[i])
            if max_fitness < population[i].fitness:
                max_fitness = population[i].fitness
        for i in range(self.data.ga_popsize):
            population[i].fitness = max_fitness - population[i].fitness

    def calc_shared_fitness(self, population, citizen):
        overall = 0
        for i in range(self.data.ga_popsize):
            diff_entries = self.problem.different_entries(citizen, population[i])
            if diff_entries < self.data.sigma_share:
                overall = overall + (1 - (diff_entries / self.data.sigma_share))
        return overall

    def blacklist(self, citizen):
        if self.data.genetic_problem == GeneticProblem.STRING_SEARCH:
            self.data.blacklist.append(citizen.str)
        elif self.data.genetic_problem == GeneticProblem.NQUEENS:
            self.data.blacklist.append(citizen.board)
        else:
            self.data.blacklist.append(citizen.knapsack)

    def are_similar(self, citizen1, citizen2):
        if self.data.genetic_problem == GeneticProblem.STRING_SEARCH:
            return self.problem.calc_similarity(citizen1, citizen2) < 2
        elif self.data.genetic_problem == GeneticProblem.NQUEENS:
            return self.problem.calc_similarity(citizen1, citizen2) < 1
        else:
            return citizen1.knapsack == citizen2.knapsack
