import numpy as np


class HyperAdaptiveStrategyDE:
    def __init__(
        self, budget=10000, population_size=100, F_base=0.6, F_range=0.4, CR=0.95, strategy="adaptive"
    ):
        self.budget = budget
        self.population_size = population_size
        self.F_base = F_base  # Base Differential weight
        self.F_range = F_range  # Range to vary F for diversity
        self.CR = CR  # Crossover probability
        self.strategy = strategy  # Strategy for mutation and selection
        self.dim = 5  # Dimensionality of the problem
        self.lb = -5.0  # Lower bound of search space
        self.ub = 5.0  # Upper bound of search space

    def __call__(self, func):
        # Initialize population randomly
        population = np.random.uniform(self.lb, self.ub, (self.population_size, self.dim))
        fitness = np.array([func(ind) for ind in population])
        evaluations = self.population_size
        best_idx = np.argmin(fitness)
        best_fitness = fitness[best_idx]
        best_individual = population[best_idx]

        # Main loop
        while evaluations < self.budget:
            for i in range(self.population_size):
                # Select mutation strategy dynamically
                if self.strategy == "adaptive":
                    idxs = np.argsort(fitness)[:2]  # Select two best for breeding
                    base = population[idxs[np.random.randint(2)]]
                else:
                    base = population[
                        np.random.choice([idx for idx in range(self.population_size) if idx != i])
                    ]

                # Dynamically adjust F with more variability
                F = self.F_base + np.random.rand() * self.F_range

                # Mutation using a different approach: DE/current-to-best/2
                idxs = [idx for idx in range(self.population_size) if idx != i]
                a, b, c, d = population[np.random.choice(idxs, 4, replace=False)]
                mutant = np.clip(
                    population[i] + F * (population[best_idx] - population[i]) + F * (a - b + c - d),
                    self.lb,
                    self.ub,
                )

                # Crossover
                cross_points = np.random.rand(self.dim) < self.CR
                if not np.any(cross_points):
                    cross_points[np.random.randint(0, self.dim)] = True
                trial = np.where(cross_points, mutant, population[i])

                # Selection
                f_trial = func(trial)
                evaluations += 1
                if f_trial < fitness[i]:
                    population[i] = trial
                    fitness[i] = f_trial
                    if f_trial < best_fitness:
                        best_idx = i
                        best_fitness = f_trial
                        best_individual = trial

                # Exit if budget exhausted
                if evaluations >= self.budget:
                    break

        # Return the best solution found
        return best_fitness, best_individual
