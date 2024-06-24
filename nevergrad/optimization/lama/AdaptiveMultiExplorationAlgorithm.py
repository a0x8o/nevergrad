import numpy as np


class AdaptiveMultiExplorationAlgorithm:
    def __init__(self, budget=10000):
        self.budget = budget
        self.dim = 5
        self.lb = -5.0
        self.ub = 5.0

        self.initial_population_size = 50
        self.F = 0.5  # Differential weight
        self.CR = 0.9  # Crossover probability
        self.local_search_chance = 0.2  # Probability to perform local search
        self.elite_ratio = 0.1  # Ratio of elite members to retain

    def __call__(self, func):
        # Initialize population
        population = np.random.uniform(self.lb, self.ub, (self.initial_population_size, self.dim))
        fitness = np.array([func(ind) for ind in population])

        self.f_opt = np.min(fitness)
        self.x_opt = population[np.argmin(fitness)]

        evaluations = self.initial_population_size

        while evaluations < self.budget:
            # Sort population based on fitness
            sorted_indices = np.argsort(fitness)
            elite_size = int(self.elite_ratio * len(population))
            elite_population = population[sorted_indices[:elite_size]]

            new_population = []
            for i in range(len(population)):
                if np.random.rand() < self.local_search_chance:
                    candidate = self.local_search(population[i], func)
                else:
                    # Mutation step
                    idxs = np.random.choice(len(population), 3, replace=False)
                    a, b, c = population[idxs]
                    mutant = np.clip(a + self.F * (b - c), self.lb, self.ub)

                    # Crossover step
                    crossover = np.random.rand(self.dim) < self.CR
                    candidate = np.where(crossover, mutant, population[i])

                # Selection step
                f_candidate = func(candidate)
                evaluations += 1
                if f_candidate < fitness[i]:
                    new_population.append(candidate)
                    if f_candidate < self.f_opt:
                        self.f_opt = f_candidate
                        self.x_opt = candidate
                else:
                    new_population.append(population[i])

                if evaluations >= self.budget:
                    break

            population = np.array(new_population)
            fitness = np.array([func(ind) for ind in population])

            # Add elite back to population
            population = np.vstack((population, elite_population))
            fitness = np.array([func(ind) for ind in population])
            evaluations += elite_size

            # Adaptive control of parameters
            self.adaptive_F_CR(evaluations)

        return self.f_opt, self.x_opt

    def local_search(self, x, func):
        best_x = x.copy()
        best_f = func(x)

        for _ in range(10):  # Local search iterations
            for i in range(self.dim):
                x_new = best_x.copy()
                step_size = np.random.uniform(-0.1, 0.1)
                x_new[i] = np.clip(best_x[i] + step_size, self.lb, self.ub)
                f_new = func(x_new)

                if f_new < best_f:
                    best_x = x_new
                    best_f = f_new

        return best_x

    def adaptive_F_CR(self, evaluations):
        # Adaptive parameters adjustment
        if evaluations % 100 == 0:
            self.F = np.random.uniform(0.4, 0.9)
            self.CR = np.random.uniform(0.1, 0.9)
            self.local_search_chance = np.random.uniform(0.1, 0.3)
