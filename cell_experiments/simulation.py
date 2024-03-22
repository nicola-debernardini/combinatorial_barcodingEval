import factory, sys, time
from boolkit import reduce, Logical
from typing import Callable
from multiprocessing import Pool

"""
python 3.10
A script that, given the number of iterations, the number of cells, and the number of barcode in the sets, 
compute the probability of having two different cells with the same label.

Description
----------
The script iterates (based on the # of iter) the labelling of # cells with random combinations of barcodes. 
The total number of labels depend on the size and number of each barcode set (e.g. [16, 48, 48, 48]).
Then, it calculates within each iteration if there was at least an event in which 2 cells were labeled identically, 
and estimates the probability of double labelling based on the number of collesions/total iterations.

Methods
-------
show()
    Pretty prints the generated factory

create_label()
    Creates a randomly generated label which mimics the process of an object being randomly
    distributed to a labeling system for each zone in a sequential manner
"""

# Simple validation function for command line arguments
def validate_args(args: list[str]) -> tuple[int, list[int], int]:

    # TODO: throw meaningful error when casting to Int a bad input (such as a String)
    
    n_sims = int(args[0]) if len(args) >= 1 else 1000000
    n_cells = int(args[1]) if len(args) >= 2 else 1000
    zones = [int(z) for z in args[2:]] if len(args) >= 3 else [16, 48, 48, 48]
    
    assert n_cells > 0, "Number of cells must be positive integer."
    assert all(n_label_sys > 0 for n_label_sys in zones), "Number of labeling systems for each zone must be positive integers."
    
    print(f"\nNumber of simulations:\t\t{n_sims}\nNumber of cells:\t\t{n_cells}\nZones:\t\t\t\t{zones}")
    return n_sims, zones, n_cells

# Define probability events
def probability_events_2(cell_values: list[int]) -> list[bool]:
    return [2 in cell_values]
def probability_events_01mill(cell_values: list[int]) -> list[bool]:
    return [cell_values.count(2)/num_cells > 0.0001]
def probability_events_1mill(cell_values: list[int]) -> list[bool]:
    return [cell_values.count(2)/num_cells > 0.001]
def probability_events_1cent(cell_values: list[int]) -> list[bool]:
    return [cell_values.count(2)/num_cells > 0.01]
def probability_events_10cent(cell_values: list[int]) -> list[bool]:
    return [cell_values.count(2)/num_cells > 0.1]
    # return [2 in cell_values] # the even that specifies that there is at least one occurrence of exactly two cells having the same label

    # Another example: return [cell_values.count(2) == 1, len(set(cell_values).intersection({1, 2})) == 2, len(set(cell_values)) == 2]
    # The above are 2 events: the first ensures that there is exactly one occurrence of two cells having the same label
    # while the second and third ensure that at most two cells have the same label


# A run of an experiment that aims to calculate the probability of some specified events.
def run_experiment(factory: factory.Factory, n_cells: int, events: Callable[[list[int]], list[bool]]) -> int: 
    cells = {}

    for _ in range(n_cells):
        cell_label = factory.create_label()
        if cell_label in cells:
            cells[cell_label] += 1
        else:
            cells[cell_label] = 1

    if reduce(events(list(cells.values())), Logical.AND):
        return 1
    return 0

if __name__ == '__main__':
    # Get the input (e.g. 10000 1000 48 48 48) 
    (simulations, zones, num_cells) = validate_args(sys.argv[1:])
    
    # Create Factory
    myFactory = factory.Factory(zones)
    start_sim_time = time.time()

    # Simulation in parallel (uses all available threads)
    with Pool() as pool:
        results_2 = pool.starmap(run_experiment, [(myFactory, num_cells, probability_events_2)] * simulations)
        results_01mill = pool.starmap(run_experiment, [(myFactory, num_cells, probability_events_01mill)] * simulations)
        results_1mill = pool.starmap(run_experiment, [(myFactory, num_cells, probability_events_1mill)] * simulations)
        results_1cent = pool.starmap(run_experiment, [(myFactory, num_cells, probability_events_1cent)] * simulations)
        results_10cent = pool.starmap(run_experiment, [(myFactory, num_cells, probability_events_10cent)] * simulations)

    collisions = sum(results_2)

    # print(f"\nCollisions:\t\t\t{collisions}\nProbability:\t\t\t{collisions / simulations}\t* probability of having at least one event with duplicated labelling\nElapsed time:\t\t\t{round(time.time() - start_sim_time, 2)} seconds.")
    print(f"""\n
          Collisions:\t\t\t{sum(results_2)}\n
          Probability:\t\t\t{sum(results_2) / simulations}\t* probability of having at least one event with duplicated labelling\n
          Collisions:\t\t\t{sum(results_01mill)}\n
          Probability:\t\t\t{sum(results_01mill) / simulations}\t* probability of having more than 0.1‰ of cells with duplicated labelling\n
          Collisions:\t\t\t{sum(results_1mill)}\n
          Probability:\t\t\t{sum(results_1mill) / simulations}\t* probability of having more than 1‰ of cells with duplicated labelling\n
          Collisions:\t\t\t{sum(results_1cent)}\n
          Probability:\t\t\t{sum(results_1cent) / simulations}\t* probability of having more than 1% of cells with duplicated labelling\n
          Collisions:\t\t\t{sum(results_10cent)}\n
          Probability:\t\t\t{sum(results_10cent) / simulations}\t* probability of having more than 10% of cells with duplicated labelling\n
          Elapsed time:\t\t\t{round(time.time() - start_sim_time, 2)} seconds.""")