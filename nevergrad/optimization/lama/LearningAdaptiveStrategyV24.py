import numpy as np


class LearningAdaptiveStrategyV24:
    def __init__(self, budget, dimension=5, population_size=100, F_init=0.5, CR_init=0.9, switch_ratio=0.5):
        self.budget = budget
        self.dimension = dimension
        self.pop_size = population_size
        self.F = F_init
        self.CR = CR_init
        self.switch_ratio = switch_ratio
        self.lower_bounds = -5.0 * np.ones(self.dimension)
        self.upper_bounds = 5.0 * np.ones(self.dimension)

    def initialize_population(self):
        return np.random.uniform(self.lower_bounds, self.upper_bounds, (self.pop_size, self.dimension))

    def mutate(self, population, best_idx, index, phase, adaptive_factors):
        size = len(population)
        idxs = [idx for idx in range(size) if idx != index]
        a, b, c = np.random.choice(idxs, 3, replace=False)
        mutation_factor = adaptive_factors["mutation"]
        if phase == 1:
            mutant = population[best_idx] + mutation_factor * (population[a] - population[b])
        else:
            d, e = np.random.choice(idxs, 2, replace=False)
            mutant = population[a] + mutation_factor * (
                population[b] - population[c] + 0.5 * (population[d] - population[e])
            )
        return np.clip(mutant, self.lower_bounds, self.upper_bounds)

    def crossover(self, target, mutant, adaptive_factors):
        CR_val = adaptive_factors["crossover"]
        crossover_mask = np.random.rand(self.dimension) < CR_val
        return np.where(crossover_mask, mutant, target)

    def select(self, target, trial, func):
        f_target = func(target)
        f_trial = func(trial)
        return (trial, f_trial) if f_trial < f_target else (target, f_target)

    def learn_parameters(self, performance_history):
        # Adapt mutation and crossover rates based on performance history
        avg_performance = np.mean(performance_history)
        return {
            "mutation": np.clip(0.5 + 0.5 * np.sin(2 * np.pi * avg_performance), 0.1, 1),
            "crossover": np.clip(0.5 + 0.5 * np.cos(2 * np.pi * avg_performance), 0.1, 1),
        }

    def __call__(self, func):
        population = self.initialize_population()
        fitnesses = np.array([func(ind) for ind in population])
        performance_history = []
        evaluations = len(population)
        best_idx = np.argmin(fitnesses)
        switch_point = int(self.switch_ratio * self.budget)
        adaptive_factors = {"mutation": self.F, "crossover": self.CR}

        while evaluations < self.budget:
            phase = 1 if evaluations < switch_point else 2
            for i in range(self.pop_size):
                mutant = self.mutate(population, best_idx, i, phase, adaptive_factors)
                trial = self.crossover(population[i], mutant, adaptive_factors)
                trial, trial_fitness = self.select(population[i], trial, func)
                evaluations += 1

                if trial_fitness < fitnesses[i]:
                    population[i] = trial
                    fitnesses[i] = trial_fitness
                    if trial_fitness < fitnesses[best_idx]:
                        best_idx = i

                if evaluations >= self.budget:
                    break

            performance_history.append(fitnesses[best_idx])
            adaptive_factors = self.learn_parameters(performance_history)

        best_fitness = fitnesses[best_idx]
        best_solution = population[best_idx]
        return best_fitness, best_solution
