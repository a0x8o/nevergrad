import numpy as np
from scipy.optimize import minimize


class OptimizedRefinedAdaptiveMultiStrategyDE:
    def __init__(self, budget=10000, dim=5):
        self.budget = budget
        self.dim = dim
        self.pop_size = 60
        self.initial_mutation_factor = 0.8
        self.final_mutation_factor = 0.3
        self.initial_crossover_prob = 0.9
        self.final_crossover_prob = 0.4
        self.elitism_rate = 0.25
        self.local_search_prob = 0.2
        self.archive = []
        self.tol = 1e-6
        self.stagnation_threshold = 10
        self.restart_threshold = 20

    def __call__(self, func):
        self.f_opt = np.inf
        self.x_opt = None
        lower_bound = -5.0
        upper_bound = 5.0

        # Initialize population
        pop = np.random.uniform(lower_bound, upper_bound, (self.pop_size, self.dim))
        fitness = np.array([func(ind) for ind in pop])
        self.budget -= self.pop_size

        generation = 0
        last_best_fitness = np.inf
        stagnation_count = 0

        while self.budget > 0:
            # Check for stagnation
            if np.abs(self.f_opt - last_best_fitness) < self.tol:
                stagnation_count += 1
            else:
                stagnation_count = 0

            # Restart population if stagnation or budget threshold reached
            if stagnation_count >= self.stagnation_threshold or self.budget < self.restart_threshold:
                pop = np.random.uniform(lower_bound, upper_bound, (self.pop_size, self.dim))
                fitness = np.array([func(ind) for ind in pop])
                self.budget -= self.pop_size
                stagnation_count = 0

            # Adaptive mutation and crossover factors
            success_rate = max(0, (self.budget - self.pop_size * generation) / self.budget)
            mutation_factor = self.initial_mutation_factor - (
                (self.initial_mutation_factor - self.final_mutation_factor) * success_rate
            )
            crossover_prob = self.initial_crossover_prob - (
                (self.initial_crossover_prob - self.final_crossover_prob) * success_rate
            )

            # Elitism: preserve top individuals
            elite_count = max(1, int(self.elitism_rate * self.pop_size))
            elite_indices = np.argsort(fitness)[:elite_count]
            elite_pop = pop[elite_indices]
            elite_fitness = fitness[elite_indices]

            new_pop = []
            for i in range(self.pop_size):
                if self.budget <= 0:
                    break

                # Enhanced selection strategy
                if np.random.rand() < 0.5:
                    idxs = np.random.choice(range(self.pop_size), 3, replace=False)
                    x1, x2, x3 = pop[idxs]
                else:
                    idxs = np.random.choice(elite_count, 3, replace=False)
                    x1, x2, x3 = elite_pop[idxs]

                # Hybrid mutation strategy based on success rate
                if success_rate < 0.3:
                    mutant = x1 + mutation_factor * (x2 - x3)
                elif success_rate < 0.6:
                    mutant = x1 + mutation_factor * (x2 - pop[np.random.randint(self.pop_size)])
                else:
                    mutant = x1 + mutation_factor * (elite_pop[np.random.randint(elite_count)] - x3)

                mutant = np.clip(mutant, lower_bound, upper_bound)

                cross_points = np.random.rand(self.dim) < crossover_prob
                if not np.any(cross_points):
                    cross_points[np.random.randint(0, self.dim)] = True
                trial = np.where(cross_points, mutant, pop[i])

                # Introduce elitist guidance in crossover stage
                trial = trial + np.random.rand(self.dim) * (elite_pop[np.random.randint(elite_count)] - trial)
                trial = np.clip(trial, lower_bound, upper_bound)

                # Local search phase with some probability
                if np.random.rand() < self.local_search_prob:
                    trial = self.local_search(trial, func)

                f_trial = func(trial)
                self.budget -= 1
                if f_trial < fitness[i]:
                    new_pop.append(trial)
                    fitness[i] = f_trial
                    if f_trial < self.f_opt:
                        self.f_opt = f_trial
                        self.x_opt = trial
                else:
                    new_pop.append(pop[i])

            # Archive mechanism with diversity preservation
            self.update_archive(new_pop)
            if len(self.archive) > self.pop_size:
                self.archive = self.archive[-self.pop_size :]

            if self.budget % int(self.pop_size * 0.1) == 0 and self.archive:
                archive_idx = np.random.choice(len(self.archive))
                archive_ind = np.array(self.archive[archive_idx])
                f_archive = func(archive_ind)
                self.budget -= 1
                if f_archive < self.f_opt:
                    self.f_opt = f_archive
                    self.x_opt = archive_ind

            new_pop = np.array(new_pop)
            combined_pop = np.vstack((elite_pop, new_pop[elite_count:]))
            combined_fitness = np.hstack((elite_fitness, fitness[elite_count:]))

            pop = combined_pop
            fitness = combined_fitness

            last_best_fitness = self.f_opt
            generation += 1

        return self.f_opt, self.x_opt

    def local_search(self, x, func):
        best_x = x.copy()
        best_f = func(x)

        if np.random.rand() < 0.5:
            # Nelder-Mead local search
            result = minimize(func, best_x, method="Nelder-Mead", options={"maxiter": 10, "xatol": 1e-6})
        else:
            # Gradient-based adjustment
            perturbation = 0.02 * (np.random.rand(self.dim) - 0.5)
            result = minimize(func, best_x + perturbation, method="BFGS", options={"maxiter": 10})

        self.budget -= result.nfev
        if result.fun < best_f:
            best_x = result.x
            best_f = result.fun

        return best_x

    def update_archive(self, new_pop):
        unique_archive = []
        for ind in new_pop:
            if not any(np.array_equal(ind, arch) for arch in self.archive):
                unique_archive.append(ind)
        self.archive.extend(unique_archive)
