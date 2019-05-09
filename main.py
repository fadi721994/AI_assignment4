from genetic_algorithm import GeneticAlgorithm
import utils
from data import Data
import os
import cProfile, pstats, io


def main():
    utils.delete_files()
    data = Data()
    algorithm = GeneticAlgorithm(data)
    algorithm.run()
    print("Finished!")

# pr = cProfile.Profile()
# pr.enable()
main()
# pr.disable()
# s = io.StringIO()
# sortby = 'cumulative'
# ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
# ps.print_stats()
# print(s.getvalue())
