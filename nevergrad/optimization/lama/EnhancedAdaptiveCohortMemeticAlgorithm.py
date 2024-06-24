import numpy as np


class EnhancedAdaptiveCohortMemeticAlgorithm:
    def __init__(self, budget=10000):
        self.budget = budget
        self.dim = 5
        self.lb = -5.0
        self.ub = 5.0

        # Parameters
        self.initial_population_size = 100
        self.elite_ratio = 0.1
        self.local_search_chance = 0.2
        self.crossover_probability = 0.9
        self.mutation_factor = 0.8
        self.global_mutation_factor = 0.5
        self.diversity_threshold = 0.2
        self.reinitialization_rate = 0.1
        self.diversity_cycle = 50
        self.local_search_intensity = 5
        self.global_search_intensity = 10

        # New parameters
        self.local_search_radius = 0.1
        self.global_search_radius = 0.5
        self.reduction_factor = 0.98  # To reduce the mutation factor over time
        self.mutation_scale = 0.1  # To scale the random mutations
        self.adaptive_crossover_rate = 0.5  # To adjust crossover probability based on diversity

    def __call__(self, func):
        # Initialize population
        population = np.random.uniform(self.lb, self.ub, (self.initial_population_size, self.dim))
        fitness = np.array([func(ind) for ind in population])

        self.f_opt = np.min(fitness)
        self.x_opt = population[np.argmin(fitness)]

        evaluations = self.initial_population_size
        diversity_counter = 0

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
                    # Differential Evolution mutation and crossover
                    idxs = np.random.choice(len(population), 3, replace=False)
                    a, b, c = population[idxs]
                    mutant = np.clip(a + self.mutation_factor * (b - c), self.lb, self.ub)

                    crossover = np.random.rand(self.dim) < self.crossover_probability
                    candidate = np.where(crossover, mutant, population[i])

                # Selection
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

            # Adaptive control of parameters based on population diversity
            diversity_counter += 1
            if diversity_counter % self.diversity_cycle == 0:
                self.adaptive_population_control(population, evaluations)

        return self.f_opt, self.x_opt

    def local_search(self, x, func):
        best_x = x.copy()
        best_f = func(x)

        for _ in range(self.local_search_intensity):
            step_size = np.random.normal(0, self.local_search_radius, size=self.dim)
            x_new = np.clip(best_x + step_size, self.lb, self.ub)
            f_new = func(x_new)

            if f_new < best_f:
                best_x = x_new
                best_f = f_new

        return best_x

    def adaptive_population_control(self, population, evaluations):
        diversity = np.mean(np.std(population, axis=0))

        if diversity < self.diversity_threshold:
            num_reinit = int(self.reinitialization_rate * len(population))
            reinit_indices = np.random.choice(len(population), num_reinit, replace=False)

            for idx in reinit_indices:
                population[idx] = np.random.uniform(self.lb, self.ub, self.dim)

        remaining_budget_ratio = (self.budget - evaluations) / self.budget
        self.local_search_chance = max(0.1, self.local_search_chance * remaining_budget_ratio)
        self.crossover_probability = self.crossover_probability * (1 + 0.1 * remaining_budget_ratio)
        self.mutation_factor = self.mutation_factor * (1 + 0.1 * remaining_budget_ratio)

        # New adaptation strategies
        self.crossover_probability *= self.adaptive_crossover_rate
        self.mutation_factor *= self.reduction_factor
        self.global_mutation_factor *= self.reduction_factor
        self.local_search_radius *= self.reduction_factor

        if diversity < self.diversity_threshold / 2 and remaining_budget_ratio > 0.5:
            self.global_search_reset(population, func)

    def global_search_reset(self, population, func):
        global_search_population = np.random.uniform(
            self.lb, self.ub, (self.global_search_intensity, self.dim)
        )

        for ind in global_search_population:
            f_ind = func(ind)
            if f_ind < self.f_opt:
                self.f_opt = f_ind
                self.x_opt = ind

        population[: self.global_search_intensity] = global_search_population
