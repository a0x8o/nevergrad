import numpy as np


class QuantumOrbitalEnhancedCrossoverOptimizerV22:
    def __init__(self, budget=10000):
        self.budget = budget
        self.dim = 5  # Dimensionality of the problem
        self.pop_size = 150  # Further refining population size
        self.sigma_initial = 0.5  # Initial mutation spread
        self.sigma_final = 0.001  # Further reduced final mutation spread
        self.CR_initial = 0.9  # Initial crossover probability
        self.CR_final = 0.1  # Lower final crossover rate to ensure diversity
        self.elitism_factor = 0.1  # Increased elitism factor
        self.q_impact_initial = 0.05  # Initial quantum impact
        self.q_impact_final = 2.5  # Increased final quantum impact for robust exploitation
        self.q_impact_increase_rate = 0.03  # Increased rate of quantum impact growth
        self.harmonic_impulse_frequency = 0.025  # Reduced frequency for harmonic impulse
        self.impulse_amplitude = 0.3  # Reduced impulse amplitude for stability

    def __call__(self, func):
        # Initialize population and fitness
        pop = np.random.uniform(-5.0, 5.0, (self.pop_size, self.dim))
        fitness = np.array([func(ind) for ind in pop])

        # Identify initial best solution
        best_idx = np.argmin(fitness)
        best_fitness = fitness[best_idx]
        best_ind = pop[best_idx].copy()

        # Evolution parameters initialization
        sigma = self.sigma_initial
        CR = self.CR_initial
        q_impact = self.q_impact_initial

        # Evolution loop
        for iteration in range(self.budget // self.pop_size):
            elite_size = int(self.elitism_factor * self.pop_size)

            for i in range(self.pop_size):
                if i < elite_size:  # Elite individuals are passed unchanged
                    continue

                # Mutation and Crossover
                idxs = [idx for idx in range(self.pop_size) if idx != i]
                a, b, c = pop[np.random.choice(idxs, 3, replace=False)]
                impulse = self.impulse_amplitude * np.sin(
                    2 * np.pi * self.harmonic_impulse_frequency * iteration
                )
                mutant = a + sigma * (b - c) + q_impact * (np.cos(c) * (b - a) + impulse)
                mutant = np.clip(mutant, -5.0, 5.0)

                # Crossover
                cross_points = np.random.rand(self.dim) < CR
                if not np.any(cross_points):
                    cross_points[np.random.randint(0, self.dim)] = True
                trial = np.where(cross_points, mutant, pop[i])

                # Selection
                trial_fitness = func(trial)
                if trial_fitness < fitness[i]:
                    pop[i] = trial
                    fitness[i] = trial_fitness
                    if trial_fitness < best_fitness:
                        best_fitness = trial_fitness
                        best_ind = trial.copy()

            # Adaptive parameter updates
            sigma *= (self.sigma_final / self.sigma_initial) ** (1 / (self.budget / self.pop_size))
            CR = max(self.CR_final, CR - (self.CR_initial - self.CR_final) / (self.budget / self.pop_size))
            q_impact = min(self.q_impact_final, q_impact + self.q_impact_increase_rate)

        return best_fitness, best_ind
