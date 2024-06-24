import numpy as np


class RefinedEnhancedHyperStrategicOptimizerV57:
    def __init__(
        self,
        budget=10000,
        population_size=135,
        F_base=0.58,
        F_range=0.42,
        CR=0.92,
        elite_fraction=0.12,
        mutation_strategy="adaptive",
    ):
        self.budget = budget
        self.population_size = population_size
        self.F_base = F_base  # Optimized base mutation factor for balanced mutation
        self.F_range = F_range  # Reduced mutation range for improved solution stability
        self.CR = CR  # Adjusted crossover probability for better exploration-exploitation trade-off
        self.elite_fraction = (
            elite_fraction  # Increased elite fraction for more focused search on promising areas
        )
        self.mutation_strategy = (
            mutation_strategy  # Adaptive mutation strategy for dynamic adaptation to problem landscape
        )
        self.dim = 5  # Dimensionality of the problem
        self.lb = -5.0  # Lower bound of search space
        self.ub = 5.0  # Upper bound of search space

    def __call__(self, func):
        # Initialize population uniformly within the search bounds
        population = np.random.uniform(self.lb, self.ub, (self.population_size, self.dim))
        fitness = np.array([func(ind) for ind in population])
        evaluations = self.population_size
        best_idx = np.argmin(fitness)
        best_fitness = fitness[best_idx]
        best_individual = population[best_idx]

        # Main optimization loop
        while evaluations < self.budget:
            elite_size = int(self.elite_fraction * self.population_size)
            elite_indices = np.argsort(fitness)[:elite_size]

            for i in range(self.population_size):
                # Decide base vector for mutation
                if self.mutation_strategy == "adaptive":
                    if np.random.rand() < 0.8:  # Adjusted probability for selecting the current best
                        base = best_individual
                    else:
                        base = population[np.random.choice(elite_indices)]
                else:
                    base = population[np.random.choice(elite_indices)]

                # Adjust mutation factor dynamically
                F = self.F_base + (2 * np.random.rand() - 1) * self.F_range

                # Mutation using DE/rand/1/bin scheme
                idxs = [idx for idx in range(self.population_size) if idx != i]
                a, b = population[np.random.choice(idxs, 2, replace=False)]
                mutant = np.clip(base + F * (a - b), self.lb, self.ub)

                # Binomial crossover
                cross_points = np.random.rand(self.dim) < self.CR
                if not np.any(cross_points):
                    cross_points[np.random.randint(0, self.dim)] = True
                trial = np.where(cross_points, mutant, population[i])

                # Evaluate and select
                f_trial = func(trial)
                evaluations += 1
                if f_trial < fitness[i]:
                    population[i] = trial
                    fitness[i] = f_trial
                    if f_trial < best_fitness:
                        best_fitness = f_trial
                        best_individual = trial

                # Terminate if the budget is exhausted
                if evaluations >= self.budget:
                    break

        return best_fitness, best_individual
