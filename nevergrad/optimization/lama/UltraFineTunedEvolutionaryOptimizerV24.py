import numpy as np


class UltraFineTunedEvolutionaryOptimizerV24:
    def __init__(
        self,
        budget=10000,
        population_size=150,
        F_base=0.65,
        F_range=0.25,
        CR=0.88,
        elite_fraction=0.15,
        mutation_strategy="advanced_adaptive",
    ):
        self.budget = budget
        self.population_size = population_size
        self.F_base = F_base  # Base mutation factor
        self.F_range = F_range  # Range for mutation factor adjustment, tightened for better control
        self.CR = CR  # Crossover probability, slightly reduced to enhance exploration
        self.elite_fraction = elite_fraction  # Fraction of top performers considered elite
        self.mutation_strategy = mutation_strategy  # Adaptive mutation strategy with an advanced approach
        self.dim = 5  # Dimensionality of the problem
        self.lb = -5.0  # Lower bound of search space
        self.ub = 5.0  # Upper bound of search space

    def __call__(self, func):
        # Initialize population uniformly within bounds
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
                if self.mutation_strategy == "advanced_adaptive":
                    # Use focused elite choice with a higher precision and control in selection
                    if np.random.rand() < 0.85:  # Increased likelihood to focus on the best
                        base = best_individual
                    else:
                        base = population[np.random.choice(elite_indices)]
                else:
                    # Default strategy using random elite base
                    base = population[np.random.choice(elite_indices)]

                # Fine-tuned mutation factor for more controlled exploration
                F = self.F_base + (2 * np.random.rand() - 1) * self.F_range

                # DE/rand/1 mutation scheme
                idxs = [idx for idx in range(self.population_size) if idx not in [i, best_idx]]
                a, b = population[np.random.choice(idxs, 2, replace=False)]
                mutant = np.clip(base + F * (a - b), self.lb, self.ub)

                # Binomial crossover with slightly adjusted probability
                cross_points = np.random.rand(self.dim) < self.CR
                if not np.any(cross_points):
                    cross_points[np.random.randint(0, self.dim)] = True
                trial = np.where(cross_points, mutant, population[i])

                # Fitness evaluation and potential replacement
                f_trial = func(trial)
                evaluations += 1
                if f_trial < fitness[i]:
                    population[i] = trial
                    fitness[i] = f_trial
                    if f_trial < best_fitness:
                        best_fitness = f_trial
                        best_individual = trial

                # Terminate if budget is reached
                if evaluations >= self.budget:
                    break

        return best_fitness, best_individual
