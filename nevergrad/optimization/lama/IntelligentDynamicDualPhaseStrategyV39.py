import numpy as np


class IntelligentDynamicDualPhaseStrategyV39:
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

    def mutate(self, population, best_idx, index, phase):
        size = len(population)
        idxs = [idx for idx in range(size) if idx != index]
        a, b, c = np.random.choice(idxs, 3, replace=False)
        if phase == 1:
            # Standard mutation strategy for phase 1
            mutant = population[best_idx] + self.F * (population[a] - population[b])
        else:
            # Enhanced mutation strategy for phase 2 using more vectors
            d, e = np.random.choice(idxs, 2, replace=False)
            mutant = population[a] + self.F * (
                population[b] - population[c] + 0.5 * (population[d] - population[e])
            )
        return np.clip(mutant, self.lower_bounds, self.upper_bounds)

    def crossover(self, target, mutant):
        crossover_mask = np.random.rand(self.dimension) < self.CR
        trial = np.where(crossover_mask, mutant, target)
        return trial

    def select(self, target, trial, func):
        f_target = func(target)
        f_trial = func(trial)
        return (trial, f_trial) if f_trial < f_target else (target, f_target)

    def adjust_parameters(self, iteration, total_iterations, population):
        # Dynamic parameter adjustment using a sigmoid-based function to emphasize middle-phase aggressiveness
        diversity = np.std(population)
        scale = iteration / total_iterations
        scale = 1 / (1 + np.exp(-10 * (scale - 0.5)))  # Sigmoid function for smoother transition
        self.F = np.clip(0.5 + 0.5 * np.sin(2 * np.pi * scale) * diversity, 0.1, 1)
        self.CR = np.clip(0.5 + 0.5 * np.cos(2 * np.pi * scale) * diversity, 0.1, 1)

    def __call__(self, func):
        population = self.initialize_population()
        fitnesses = np.array([func(ind) for ind in population])
        evaluations = len(population)
        iteration = 0
        best_idx = np.argmin(fitnesses)
        switch_point = int(self.switch_ratio * self.budget)

        while evaluations < self.budget:
            phase = 1 if evaluations < switch_point else 2
            self.adjust_parameters(
                iteration, switch_point if phase == 1 else self.budget - switch_point, population
            )

            for i in range(self.pop_size):
                mutant = self.mutate(population, best_idx, i, phase)
                trial = self.crossover(population[i], mutant)
                trial, trial_fitness = self.select(population[i], trial, func)
                evaluations += 1

                if trial_fitness < fitnesses[i]:
                    population[i] = trial
                    fitnesses[i] = trial_fitness
                    if trial_fitness < fitnesses[best_idx]:
                        best_idx = i

                if evaluations >= self.budget:
                    break
            iteration += 1

        best_fitness = fitnesses[best_idx]
        best_solution = population[best_idx]
        return best_fitness, best_solution
