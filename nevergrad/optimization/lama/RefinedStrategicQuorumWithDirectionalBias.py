import numpy as np


class RefinedStrategicQuorumWithDirectionalBias:
    def __init__(
        self,
        budget,
        dimension=5,
        population_size=100,
        elite_fraction=0.1,
        mutation_scale=0.3,
        elite_adaptation=0.02,
        momentum=0.8,
    ):
        self.budget = budget
        self.dimension = dimension
        self.population_size = population_size
        self.elite_count = max(1, int(population_size * elite_fraction))
        self.mutation_scale = mutation_scale
        self.elite_adaptation = elite_adaptation
        self.momentum = momentum

    def __call__(self, func):
        # Initialize population
        population = np.random.uniform(-5.0, 5.0, (self.population_size, self.dimension))
        fitness = np.array([func(individual) for individual in population])
        evaluations = self.population_size

        # Initialize best solution and momentum vector
        best_idx = np.argmin(fitness)
        best_individual = population[best_idx]
        best_fitness = fitness[best_idx]
        best_momentum = np.zeros(self.dimension)

        # Evolution loop
        while evaluations < self.budget:
            new_population = []
            for i in range(self.population_size):
                # Select a quorum randomly, including best individual
                quorum_indices = np.random.choice(self.population_size, self.elite_count - 1, replace=False)
                quorum_indices = np.append(quorum_indices, best_idx)
                quorum = population[quorum_indices]
                quorum_fitness = fitness[quorum_indices]

                # Find the local best in the quorum
                local_best_idx = np.argmin(quorum_fitness)
                local_best = quorum[local_best_idx]

                # Mutation influenced by best, local best, and momentum
                direction = best_individual - local_best
                random_direction = np.random.normal(0, self.mutation_scale, self.dimension)
                mutation = random_direction * direction + self.momentum * best_momentum
                child = np.clip(local_best + mutation, -5.0, 5.0)
                child_fitness = func(child)
                evaluations += 1

                # Update best solution and momentum
                if child_fitness < best_fitness:
                    best_momentum = child - best_individual
                    best_fitness = child_fitness
                    best_individual = child

                new_population.append(child)

                if evaluations >= self.budget:
                    break

            population = np.array(new_population)
            fitness = np.array([func(ind) for ind in population])

            # Adapt the elite count based on progress
            if self.elite_adaptation > 0:
                self.elite_count = max(
                    1, int(self.elite_count * (1 + self.elite_adaptation * np.random.uniform(-1, 1)))
                )

        return best_fitness, best_individual
