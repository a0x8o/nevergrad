import numpy as np


class DynamicAdaptiveEliteHybridOptimizer:
    def __init__(self, budget=10000):
        self.budget = budget
        self.dim = 5
        self.pop_size = 200  # Increased population size for better diversity
        self.initial_F = 0.6  # Adjusted for balanced mutation step
        self.initial_CR = 0.9  # High crossover rate to maintain genetic diversity
        self.c1 = 1.2  # Cognitive coefficient for personal best attraction
        self.c2 = 1.2  # Social coefficient for global best attraction
        self.w = 0.7  # Inertia weight for maintaining momentum
        self.elite_fraction = 0.1  # Fraction of elite population
        self.diversity_threshold = 1e-4  # Higher threshold to reinitialize earlier
        self.tau1 = 0.1  # Parameter adaptation probability
        self.tau2 = 0.1

    def initialize_population(self, bounds):
        population = np.random.uniform(bounds.lb, bounds.ub, (self.pop_size, self.dim))
        velocities = np.random.uniform(-1, 1, (self.pop_size, self.dim))
        return population, velocities

    def select_parents(self, population):
        idxs = np.random.choice(range(population.shape[0]), 3, replace=False)
        return population[idxs]

    def mutate(self, parent1, parent2, parent3, F):
        return np.clip(parent1 + F * (parent2 - parent3), -5.0, 5.0)

    def crossover(self, target, mutant, CR):
        j_rand = np.random.randint(self.dim)
        return np.where(np.random.rand(self.dim) < CR, mutant, target)

    def diversity(self, population):
        return np.mean(np.std(population, axis=0))

    def adapt_parameters(self, F, CR):
        if np.random.rand() < self.tau1:
            F = np.clip(np.random.normal(F, 0.1), 0, 1)
        if np.random.rand() < self.tau2:
            CR = np.clip(np.random.normal(CR, 0.1), 0, 1)
        return F, CR

    def __call__(self, func):
        self.f_opt = np.inf
        self.x_opt = None
        bounds = func.bounds

        population, velocities = self.initialize_population(bounds)
        personal_best_positions = np.copy(population)
        personal_best_scores = np.array([func(ind) for ind in population])
        global_best_position = personal_best_positions[np.argmin(personal_best_scores)]
        global_best_score = np.min(personal_best_scores)
        evaluations = self.pop_size

        F = self.initial_F
        CR = self.initial_CR

        while evaluations < self.budget:
            new_population = np.zeros((self.pop_size, self.dim))
            fitness = np.zeros(self.pop_size)

            for i in range(self.pop_size):
                # Parent selection and mutation
                parent1, parent2, parent3 = self.select_parents(population)
                F, CR = self.adapt_parameters(F, CR)
                mutant = self.mutate(parent1, parent2, parent3, F)
                trial = self.crossover(population[i], mutant, CR)

                trial_fitness = func(trial)
                evaluations += 1

                if trial_fitness < personal_best_scores[i]:
                    personal_best_positions[i] = trial
                    personal_best_scores[i] = trial_fitness

                if personal_best_scores[i] < global_best_score:
                    global_best_position = personal_best_positions[i]
                    global_best_score = personal_best_scores[i]

                velocities[i] = (
                    self.w * velocities[i]
                    + self.c1 * np.random.rand(self.dim) * (personal_best_positions[i] - population[i])
                    + self.c2 * np.random.rand(self.dim) * (global_best_position - population[i])
                )
                new_population[i] = population[i] + velocities[i]
                new_population[i] = np.clip(new_population[i], bounds.lb, bounds.ub)
                fitness[i] = func(new_population[i])
                evaluations += 1

            population = new_population
            if np.min(fitness) < self.f_opt:
                self.f_opt = np.min(fitness)
                self.x_opt = population[np.argmin(fitness)]

            # Elite selection for local search
            elite_count = max(1, int(self.elite_fraction * self.pop_size))
            elite_indices = np.argsort(fitness)[:elite_count]
            elite_population = population[elite_indices]
            elite_velocities = velocities[elite_indices]

            for idx in range(elite_count):
                local_search_budget = min(
                    30, self.budget - evaluations
                )  # Increased iterations for better local search
                for _ in range(local_search_budget):
                    trial = np.clip(
                        elite_population[idx] + np.random.randn(self.dim) * 0.01, bounds.lb, bounds.ub
                    )  # Reduced perturbation for precision
                    trial_fitness = func(trial)
                    evaluations += 1
                    if trial_fitness < fitness[elite_indices[idx]]:
                        elite_population[idx] = trial
                        fitness[elite_indices[idx]] = trial_fitness
                    if evaluations >= self.budget:
                        break

            # Reinitialization if diversity is too low
            if self.diversity(population) < self.diversity_threshold:
                population, velocities = self.initialize_population(bounds)
                personal_best_positions = np.copy(population)
                personal_best_scores = np.array([func(ind) for ind in population])
                global_best_position = personal_best_positions[np.argmin(personal_best_scores)]
                global_best_score = np.min(personal_best_scores)
                evaluations += self.pop_size
            else:
                # Update population with elite individuals
                population[:elite_count] = elite_population
                velocities[:elite_count] = elite_velocities

                # Replace worst individuals with random samples for maintaining diversity
                worst_indices = np.argsort(fitness)[-elite_count:]
                population[worst_indices] = np.random.uniform(bounds.lb, bounds.ub, (elite_count, self.dim))

        return self.f_opt, self.x_opt
