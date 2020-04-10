from mlrose import TravellingSales, TSPOpt, genetic_alg

def tsp(distances=None, num_of_nodes=None):
    '''https://mlrose.readthedocs.io/en/stable/source/tutorial2.html'''

    fitness_coordinates = TravellingSales(distances=distances)
    problem_fit = TSPOpt(length=num_of_nodes, fitness_fn=fitness_coordinates, maximize=False)
    best_route, _ = genetic_alg(problem_fit, random_state=2)
    return best_route
