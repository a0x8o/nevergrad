import numpy as np


class ImprovedDualPhaseAdaptiveMemoryStrategyV58:
    def __init__(
        self,
        budget,
        dimension=5,
        population_size=100,
        F_init=0.5,
        CR_init=0.9,
        switch_ratio=0.5,
        memory_size=20,
    ):
        self.budget = budget
        self.dimension = dimension
        self.pop_size = population_size
        self.F = F_init
        self.CR = CR_init
        self.switch_ratio = switch_ratio
        self.memory_size = memory_size
        self.lower_bounds = -5.0 * np.ones(self.dimension)
        self.upper_bounds = 5.0 * np.ones(self.dimension)
        self.memory = []

    def initialize_population(self):
        return np.random.uniform(self.lower_bounds, self.upper_bounds, (self.pop_size, self.dimension))

    def mutate(self, population, best_idx, index, phase):
        size = len(population)
        idxs = [idx for idx in range(size) if idx != index]
        a, b, c = np.random.choice(idxs, 3, replace=False)
        if phase == 1:
            # Standard differential mutation
            mutant = population[a] + self.F * (population[b] - population[c])
        else:
            # Memory-guided mutation
            memory_effect = np.mean(self.memory, axis=0) if self.memory else np.zeros(self.dimension)
            mutant = population[a] + self.F * (population[best_idx] - population[a]) + memory_effect

        return np.clip(mutant, self.lower_bounds, self.upper_bounds)

    def crossover(self, target, mutant):
        crossover_mask = np.random.rand(self.dimension) < self.CR
        return np.where(crossover_mask, mutant, target)

    def select(self, target, trial, func):
        f_target = func(target)
        f_trial = func(trial)
        if f_trial < f_target:
            self.memory.append(trial - target)
            if len(self.memory) > self.memory_size:
                self.memory.pop(0)
            return trial, f_trial
        else:
            return target, f_target

    def __call__(self, func):
        population = self.initialize_population()
        fitnesses = np.array([func(ind) for ind in population])
        evaluations = len(population)
        best_idx = np.argmin(fitnesses)
        switch_point = int(self.switch_ratio * self.budget)

        while evaluations < self.budget:
            phase = 1 if evaluations < switch_point else 2
            for i in range(self.pop_size):
                mutant = self.mutate(population, best_idx, i, phase)
                trial = self.crossover(population[i], mutant)
                population[i], fitnesses[i] = self.select(population[i], trial, func)
                evaluations += 1

                if fitnesses[i] < fitnesses[best_idx]:
                    best_idx = i

                if evaluations >= self.budget:
                    break

        best_fitness = fitnesses[best_idx]
        best_solution = population[best_idx]
        return best_fitness, best_solution
