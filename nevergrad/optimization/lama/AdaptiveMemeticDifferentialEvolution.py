import numpy as np
from scipy.optimize import minimize


class AdaptiveMemeticDifferentialEvolution:
    def __init__(self, budget=10000):
        self.budget = budget
        self.dim = 5
        self.lb = -5.0
        self.ub = 5.0
        self.pop_size = 100
        self.F = 0.5
        self.CR = 0.9
        self.local_search_prob = 0.1
        self.restart_threshold = 50
        self.strategy_weights = np.ones(4)
        self.strategy_success = np.zeros(4)
        self.learning_rate = 0.1
        self.no_improvement_count = 0
        self.history = []

    def _initialize_population(self):
        return np.random.uniform(self.lb, self.ub, (self.pop_size, self.dim))

    def _local_search(self, x, func):
        x_local, f_local = minimize(
            func, x, method="L-BFGS-B", bounds=[(self.lb, self.ub)] * self.dim
        ).x, func(x)
        return x_local, f_local

    def _dynamic_parameters(self):
        self.F = np.clip(self.F + np.random.normal(0, self.learning_rate), 0.1, 1.0)
        self.CR = np.clip(self.CR + np.random.normal(0, self.learning_rate), 0.1, 1.0)

    def _mutation_best_1(self, population, best_idx, r1, r2):
        return population[best_idx] + self.F * (population[r1] - population[r2])

    def _mutation_rand_1(self, population, r1, r2, r3):
        return population[r1] + self.F * (population[r2] - population[r3])

    def _mutation_rand_2(self, population, r1, r2, r3, r4, r5):
        return (
            population[r1]
            + self.F * (population[r2] - population[r3])
            + self.F * (population[r4] - population[r5])
        )

    def _mutation_best_2(self, population, best_idx, r1, r2, r3, r4):
        return (
            population[best_idx]
            + self.F * (population[r1] - population[r2])
            + self.F * (population[r3] - population[r4])
        )

    def _select_strategy(self):
        return np.random.choice(
            [self._mutation_best_1, self._mutation_rand_1, self._mutation_rand_2, self._mutation_best_2],
            p=self.strategy_weights / self.strategy_weights.sum(),
        )

    def _opposition_based_learning(self, population):
        return self.lb + self.ub - population

    def _crowding_distance(self, population, fitness):
        distances = np.zeros(len(population))
        sorted_indices = np.argsort(fitness)
        for i in range(self.dim):
            sorted_pop = population[sorted_indices, i]
            distances[sorted_indices[0]] = distances[sorted_indices[-1]] = float("inf")
            for j in range(1, len(population) - 1):
                distances[sorted_indices[j]] += (sorted_pop[j + 1] - sorted_pop[j - 1]) / (
                    sorted_pop[-1] - sorted_pop[0] + 1e-12
                )
        return distances

    def __call__(self, func):
        population = self._initialize_population()
        fitness = np.array([func(ind) for ind in population])
        self.evaluations = len(population)

        self.f_opt = np.min(fitness)
        self.x_opt = population[np.argmin(fitness)].copy()

        while self.evaluations < self.budget:
            new_population = []
            new_fitness = []

            for i in range(self.pop_size):
                if self.evaluations >= self.budget:
                    break

                strategy = self._select_strategy()
                indices = [idx for idx in range(self.pop_size) if idx != i]
                r1, r2, r3, r4, r5 = np.random.choice(indices, 5, replace=False)
                best_idx = np.argmin(fitness)

                if strategy == self._mutation_best_1:
                    donor = self._mutation_best_1(population, best_idx, r1, r2)
                elif strategy == self._mutation_rand_1:
                    donor = self._mutation_rand_1(population, r1, r2, r3)
                elif strategy == self._mutation_rand_2:
                    donor = self._mutation_rand_2(population, r1, r2, r3, r4, r5)
                else:  # strategy == self._mutation_best_2
                    donor = self._mutation_best_2(population, best_idx, r1, r2, r3, r4)

                trial = np.clip(donor, self.lb, self.ub)
                f_trial = func(trial)
                self.evaluations += 1

                if f_trial < fitness[i]:
                    new_population.append(trial)
                    new_fitness.append(f_trial)
                    strategy_idx = [
                        self._mutation_best_1,
                        self._mutation_rand_1,
                        self._mutation_rand_2,
                        self._mutation_best_2,
                    ].index(strategy)
                    self.strategy_success[strategy_idx] += 1
                    if f_trial < self.f_opt:
                        self.f_opt = f_trial
                        self.x_opt = trial
                        self.no_improvement_count = 0
                else:
                    new_population.append(population[i])
                    new_fitness.append(fitness[i])

            population = np.array(new_population)
            fitness = np.array(new_fitness)

            if np.random.rand() < self.local_search_prob:
                elite_indices = np.argsort(fitness)[: int(0.1 * self.pop_size)]
                for idx in elite_indices:
                    if self.evaluations >= self.budget:
                        break
                    x_local, f_local = self._local_search(population[idx], func)
                    self.evaluations += 1
                    if f_local < fitness[idx]:
                        population[idx] = x_local
                        fitness[idx] = f_local
                        if f_local < self.f_opt:
                            self.f_opt = f_local
                            self.x_opt = x_local
                            self.no_improvement_count = 0

            if self.no_improvement_count >= self.restart_threshold:
                population = self._initialize_population()
                fitness = np.array([func(ind) for ind in population])
                self.evaluations += len(population)
                self.no_improvement_count = 0

            # Adaptive strategy selection
            self.strategy_weights = self.strategy_success + 1
            self.strategy_success.fill(0)
            self.no_improvement_count += 1

            # Dynamic population resizing based on performance
            if self.no_improvement_count >= 10:
                self.pop_size = max(20, self.pop_size - 10)
                population = population[: self.pop_size]
                fitness = fitness[: self.pop_size]
                self.no_improvement_count = 0

            self._dynamic_parameters()

        return self.f_opt, self.x_opt
