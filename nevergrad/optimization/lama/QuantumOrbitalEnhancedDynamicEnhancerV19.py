import numpy as np


class QuantumOrbitalEnhancedDynamicEnhancerV19:
    def __init__(self, budget=10000):
        self.budget = budget
        self.dim = 5  # Fixed dimensionality
        self.pop_size = 1000  # Increased population size for broader exploration
        self.sigma_initial = 3.0  # Slightly higher initial mutation spread to explore more aggressively
        self.sigma_final = 0.0001  # Reduced final mutation spread for fine-tuning solutions
        self.CR_initial = 0.9  # Initial crossover probability
        self.CR_final = 0.05  # Final crossover probability for maintaining diversity
        self.elitism_factor = 0.05  # Increased elitism to preserve more good candidates
        self.q_impact_initial = 0.005  # Initial quantum impact
        self.q_impact_final = 2.0  # Increased quantum impact for stronger final exploitation
        self.q_impact_increase_rate = 0.05  # Accelerated rate of quantum impact increase
        self.harmonic_impulse_frequency = 0.25  # Higher frequency for more frequent dynamic shifts
        self.impulse_amplitude = 2.5  # Increased amplitude for stronger perturbations

    def __call__(self, func):
        # Initialize population
        pop = np.random.uniform(-5.0, 5.0, (self.pop_size, self.dim))
        fitness = np.array([func(ind) for ind in pop])

        best_idx = np.argmin(fitness)
        best_fitness = fitness[best_idx]
        best_ind = pop[best_idx].copy()

        sigma = self.sigma_initial
        CR = self.CR_initial
        q_impact = self.q_impact_initial

        # Evolution loop
        for iteration in range(self.budget // self.pop_size):
            elite_size = int(self.elitism_factor * self.pop_size)

            for i in range(self.pop_size):
                if i < elite_size:  # Elite individuals undergo smaller changes
                    continue

                idxs = [idx for idx in range(self.pop_size) if idx != i]
                a, b, c = pop[np.random.choice(idxs, 3, replace=False)]
                impulse = self.impulse_amplitude * np.sin(
                    2 * np.pi * self.harmonic_impulse_frequency * iteration
                )
                mutant = a + sigma * (b - c) + q_impact * np.sin(c + impulse) * (b - a)
                mutant = np.clip(mutant, -5.0, 5.0)

                # Crossover process
                cross_points = np.random.rand(self.dim) < CR
                if not np.any(cross_points):
                    cross_points[np.random.randint(0, self.dim)] = True
                trial = np.where(cross_points, mutant, pop[i])

                trial_fitness = func(trial)
                if trial_fitness < fitness[i]:
                    pop[i] = trial
                    fitness[i] = trial_fitness
                    if trial_fitness < best_fitness:
                        best_fitness = trial_fitness
                        best_ind = trial.copy()

            # Adaptive parameter updating
            sigma = sigma * (self.sigma_final / self.sigma_initial) ** (1 / (self.budget / self.pop_size))
            CR = max(self.CR_final, CR - (self.CR_initial - self.CR_final) / (self.budget / self.pop_size))
            q_impact = min(self.q_impact_final, q_impact + self.q_impact_increase_rate)

        return best_fitness, best_ind
