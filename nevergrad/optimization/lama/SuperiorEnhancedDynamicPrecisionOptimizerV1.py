import numpy as np


class SuperiorEnhancedDynamicPrecisionOptimizerV1:
    def __init__(self, budget=10000):
        self.budget = budget
        self.dim = 5  # Dimensionality is fixed at 5
        self.lb = -5.0  # Lower bound of search space
        self.ub = 5.0  # Upper bound of search space

    def __call__(self, func):
        # Initialize temperature and advanced cooling parameters
        T = 1.25  # Higher initial temperature for a more aggressive exploratory start
        T_min = 0.0003  # Further lowered minimum temperature for deeper fine-tuning in late stages
        alpha = 0.93  # Slower cooling rate to maximize the duration of effective search

        # Mutation and crossover parameters finely tuned for dynamic adaptability
        F = 0.77  # Slightly increased Mutation factor for more robust exploration
        CR = 0.89  # Higher Crossover probability to enhance solution diversity

        population_size = 78  # Slightly adjusted population size for more balanced computation
        pop = np.random.uniform(self.lb, self.ub, (population_size, self.dim))
        fitness = np.array([func(ind) for ind in pop])
        f_opt = np.min(fitness)
        x_opt = pop[np.argmin(fitness)]
        evaluation_count = population_size

        # Dynamic mutation factor integrations with temperature and progress-driven modifications
        while evaluation_count < self.budget and T > T_min:
            for i in range(population_size):
                indices = [idx for idx in range(population_size) if idx != i]
                a, b, c = pop[np.random.choice(indices, 3, replace=False)]
                # Dynamic mutation factor adjusted for controlled exploration-exploitation balance
                dynamic_F = (
                    F
                    * np.exp(-0.05 * T)
                    * (0.75 + 0.25 * np.tanh(4 * (evaluation_count / self.budget - 0.5)))
                )
                mutant = np.clip(a + dynamic_F * (b - c), self.lb, self.ub)
                cross_points = np.random.rand(self.dim) < CR
                trial = np.where(cross_points, mutant, pop[i])

                trial_fitness = func(trial)
                evaluation_count += 1
                delta_fitness = trial_fitness - fitness[i]

                # Enhanced probabilistic acceptance condition with a more responsive temperature adaptation
                if delta_fitness < 0 or np.random.rand() < np.exp(
                    -delta_fitness / (T * (1 + 0.07 * np.abs(delta_fitness)))
                ):
                    pop[i] = trial
                    fitness[i] = trial_fitness
                    if trial_fitness < f_opt:
                        f_opt = trial_fitness
                        x_opt = trial

            # Advanced adaptive cooling with a modulated decay factor based on search phase
            adaptive_cooling = alpha - 0.006 * np.sin(4 * np.pi * evaluation_count / self.budget)
            T *= adaptive_cooling

        return f_opt, x_opt
