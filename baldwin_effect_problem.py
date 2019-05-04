from citizen import Citizen
import random
import utils


class BaldwinEffectProblem:
    def __init__(self, data):
        self.data = data
        self.genes_num = 20
        self.learning_steps = 1000
        self.target_gene = '11010100100001101011'

    def init_citizen(self):
        citizen = Citizen()
        entries = []
        for i in range(self.genes_num):
            citizen.str = citizen.str + "-"
            entries.append(i)
        self.init_character(citizen, '?', entries)
        self.init_character(citizen, '1', entries)
        self.init_character(citizen, '0', entries)
        return citizen

    def init_character(self, citizen, character, entries):
        if character == '?':
            amount = int(self.genes_num / 2)
        else:
            amount = int(self.genes_num / 4)
        for i in range(amount):
            changed = False
            while not changed:
                entry = random.choice(entries)
                if citizen.str[entry] == '-':
                    entries.remove(entry)
                    changed = 1
                    string_list = list(citizen.str)
                    string_list[entry] = character
                    citizen.str = ''.join(string_list)

    def calc_fitness(self, population):
        for i in range(self.data.ga_popsize):
            tries_left = 0
            if self.is_solution_cadidate(population[i].str):
                for j in range(self.learning_steps):
                    updated_gene = self.update_string(population[i].str)
                    if updated_gene == self.target_gene:
                        tries_left = self.learning_steps - j
                        break
            population[i].fitness = 1 + ((19 * tries_left) / 1000)

    def is_solution_cadidate(self, citizen_gene):
        for i in range(self.genes_num):
            if citizen_gene[i] != '?' and citizen_gene[i] != self.target_gene[i]:
                return False
        return True

    def update_string(self, citizen_gene):
        assert(self.genes_num == len(citizen_gene))
        ques_marks = []
        for i, entry in enumerate(citizen_gene):
            if entry == '?':
                ques_marks.append(i)
        while len(ques_marks) > 0:
            entry = random.choice(ques_marks)
            ques_marks.remove(entry)
            bit = str(random.randint(0, 1))
            string_list = list(citizen_gene)
            string_list[entry] = bit
            citizen_gene = ''.join(string_list)
        return citizen_gene

    def print_best(self, gav, iter_num):
        print("Best: " + gav[0].str + " (" + str(gav[0].fitness) + ")")
        with open("output.txt", 'a') as file:
            file.write("Best: " + gav[0].str + " (" + str(gav[0].fitness) + ")\n")
            file.write("    Iteration number: " + str(iter_num) + "\n")
            file.write("    Fitness average: " + str(round(utils.average(gav, self.data.ga_popsize), 3)) + "\n")
            file.write("    Fitness deviation: " + str(round(utils.deviation(gav, self.data.ga_popsize), 3)) + "\n")

    def crossover(self, first_parent, second_parent):
        tsize = self.genes_num
        spos = int(random.randint(0, 32767) % tsize)
        return Citizen(first_parent.str[0:spos] + second_parent.str[spos:tsize])

    def mutate(self, citizen):
        tsize = self.genes_num
        ipos = int(random.randint(0, 32767) % tsize)
        bit = random.randint(0, 2)
        if bit == 2:
            bit = '?'
        bit = str(bit)
        string_list = list(citizen.str)
        string_list[ipos] = bit
        citizen.str = ''.join(string_list)

    def is_done(self, best):
        if '?' in best.str:
            return False
        return True
