import numpy as np


class ERADS:
    def __init__(
        self,
        budget,
        population_size=50,
        F_init=0.5,
        F_end=0.8,
        CR=0.9,
        memory_factor=0.2,
        mutation_strategy="best",
    ):
        self.budget = budget
        self.population_size = population_size
        self.F_init = F_init  # Initial differential weight
        self.F_end = F_end  # Final differential weight for linear adaptation
        self.CR = CR  # Crossover probability
        self.dimension = 5
        self.bounds = (-5.0, 5.0)  # Search space bounds
        self.memory_factor = memory_factor  # Weight given to memory in mutation
        self.mutation_strategy = mutation_strategy  # Mutation strategy: 'best' or 'rand'

    def __call__(self, func):
        # Initialize population
        population = np.random.uniform(self.bounds[0], self.bounds[1], (self.population_size, self.dimension))
        fitness = np.array([func(ind) for ind in population])
        best_index = np.argmin(fitness)
        self.f_opt = fitness[best_index]
        self.x_opt = population[best_index]
        evaluations = self.population_size
        memory = np.zeros(self.dimension)  # A single vector holds the cumulative memory

        while evaluations < self.budget:
            F_current = self.F_init + (self.F_end - self.F_init) * (evaluations / self.budget)

            for i in range(self.population_size):
                if self.mutation_strategy == "best":
                    x_base = population[best_index]
                else:
                    x_base = population[np.random.randint(0, self.population_size)]

                indices = np.random.choice(
                    [j for j in range(self.population_size) if j != i], 2, replace=False
                )
                x1, x2 = population[indices]

                # Mutant vector incorporating memory
                mutant = x_base + F_current * (x1 - x2 + self.memory_factor * memory)
                mutant = np.clip(mutant, self.bounds[0], self.bounds[1])

                # Crossover
                trial = np.where(np.random.rand(self.dimension) < self.CR, mutant, population[i])
                f_trial = func(trial)
                evaluations += 1

                # Selection and memory update
                if f_trial < fitness[i]:
                    population[i] = trial
                    fitness[i] = f_trial
                    if f_trial < self.f_opt:
                        self.f_opt = f_trial
                        self.x_opt = trial
                        best_index = i  # Update best index

                    # Update memory with the successful mutation direction scaled by F
                    memory = (1 - self.memory_factor) * memory + self.memory_factor * F_current * (
                        mutant - population[i]
                    )

                if evaluations >= self.budget:
                    break

        return self.f_opt, self.x_opt
