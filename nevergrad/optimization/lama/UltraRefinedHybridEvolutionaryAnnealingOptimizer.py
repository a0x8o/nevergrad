import numpy as np


class UltraRefinedHybridEvolutionaryAnnealingOptimizer:
    def __init__(self, budget=10000):
        self.budget = budget
        self.dim = 5  # Dimensionality is fixed at 5 as per the problem description
        self.lb = -5.0  # Lower bound as per the problem description
        self.ub = 5.0  # Upper bound as per the problem description

    def __call__(self, func):
        # Adjust initial temperature and cooling rate for optimal balance of exploration and exploitation
        T = 1.2
        T_min = 0.005  # Modify minimum temperature for a more gradual cooling
        alpha = 0.95  # Adjust cooling rate to allow more thorough exploration at higher temperatures

        # Refine mutation and crossover parameters for improved performance
        F = 0.65  # Slightly lower mutation factor to stabilize the search
        CR = 0.85  # Adjust crossover probability to ensure effective diversity maintenance

        population_size = 70  # Increase population size to improve initial coverage
        pop = np.random.uniform(self.lb, self.ub, (population_size, self.dim))
        fitness = np.array([func(ind) for ind in pop])
        f_opt = np.min(fitness)
        x_opt = pop[np.argmin(fitness)]
        evaluation_count = population_size

        # Utilize dynamic mutation factor and temperature-dependent simulated annealing acceptance
        while evaluation_count < self.budget and T > T_min:
            for i in range(population_size):
                indices = [idx for idx in range(population_size) if idx != i]
                a, b, c = pop[np.random.choice(indices, 3, replace=False)]
                # Adjust mutation factor dynamically based on both temperature and iteration progress
                dynamic_F = F * (1 - 0.05 * np.log(1 + T)) * (0.5 + 0.5 * (evaluation_count / self.budget))
                mutant = np.clip(a + dynamic_F * (b - c), self.lb, self.ub)
                cross_points = np.random.rand(self.dim) < CR
                trial = np.where(cross_points, mutant, pop[i])

                trial_fitness = func(trial)
                evaluation_count += 1
                delta_fitness = trial_fitness - fitness[i]

                # Implement a more nuanced acceptance criterion influenced by both delta_fitness and T
                if delta_fitness < 0 or np.random.rand() < np.exp(
                    -delta_fitness / (T * (1 + 0.1 * np.abs(delta_fitness)))
                ):
                    pop[i] = trial
                    fitness[i] = trial_fitness
                    if trial_fitness < f_opt:
                        f_opt = trial_fitness
                        x_opt = trial

            # Implement an adaptive cooling rate that fine-tunes based on the stage of optimization
            adaptive_cooling = alpha - 0.02 * (evaluation_count / self.budget)
            T *= adaptive_cooling

        return f_opt, x_opt
