import numpy as np


class QuantumHarmonicAdaptiveFeedbackOptimizer:
    def __init__(
        self,
        budget,
        dim=5,
        pop_size=150,
        elite_rate=0.2,
        resonance_factor=0.1,
        mutation_scale=0.1,
        harmonic_frequency=0.05,
        feedback_intensity=0.3,
        damping_factor=0.95,
        mutation_decay=0.95,
    ):
        self.budget = budget
        self.dim = dim
        self.pop_size = pop_size
        self.elite_count = int(pop_size * elite_rate)
        self.resonance_factor = resonance_factor
        self.mutation_scale = mutation_scale
        self.harmonic_frequency = harmonic_frequency
        self.feedback_intensity = feedback_intensity
        self.damping_factor = damping_factor
        self.mutation_decay = mutation_decay
        self.lower_bound = -5.0
        self.upper_bound = 5.0

    def initialize(self):
        self.population = np.random.uniform(self.lower_bound, self.upper_bound, (self.pop_size, self.dim))
        self.fitnesses = np.full(self.pop_size, np.inf)
        self.best_solution = None
        self.best_fitness = np.inf

    def evaluate_fitness(self, func):
        for i in range(self.pop_size):
            fitness = func(self.population[i])
            if fitness < self.fitnesses[i]:
                self.fitnesses[i] = fitness
                if fitness < self.best_fitness:
                    self.best_fitness = fitness
                    self.best_solution = np.copy(self.population[i])

    def quantum_mutations(self, elite_sample):
        # Enhanced dynamic quantum mutations with adaptive feedback
        harmonic_influence = self.harmonic_frequency * np.sin(np.random.uniform(0, 2 * np.pi, self.dim))
        quantum_resonance = self.resonance_factor * (np.random.uniform(-1, 1, self.dim) ** 3)
        mutation_effect = np.random.normal(0, self.mutation_scale, self.dim)
        feedback_correction = self.feedback_intensity * (self.best_solution - elite_sample)

        new_solution = (
            elite_sample + harmonic_influence + quantum_resonance + mutation_effect + feedback_correction
        )
        new_solution = np.clip(new_solution, self.lower_bound, self.upper_bound)
        return new_solution

    def update_population(self):
        # Sorted population by fitness for selective reproduction
        sorted_indices = np.argsort(self.fitnesses)
        elite_indices = sorted_indices[: self.elite_count]
        non_elite_indices = sorted_indices[self.elite_count :]

        # Generate new solutions based on elites with quantum-inspired adaptive variations
        for idx in non_elite_indices:
            elite_sample = self.population[np.random.choice(elite_indices)]
            self.population[idx] = self.quantum_mutations(elite_sample)

        # Dynamically adjust mutation parameters
        self.mutation_scale *= self.mutation_decay
        self.resonance_factor *= self.damping_factor

    def __call__(self, func):
        self.initialize()
        evaluations = 0
        while evaluations < self.budget:
            self.evaluate_fitness(func)
            self.update_population()
            evaluations += self.pop_size

        return self.best_fitness, self.best_solution
