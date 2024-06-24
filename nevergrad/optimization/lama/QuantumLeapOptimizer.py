import numpy as np


class QuantumLeapOptimizer:
    def __init__(self, budget=10000):
        self.budget = budget
        self.dim = 5  # Dimensionality of the problem

    def __call__(self, func):
        self.f_opt = np.inf
        self.x_opt = None

        # Strategy parameters
        population_size = 50  # Reduced population size for more focused exploration
        gamma_initial = 0.5  # Initial gamma for exploration/exploitation balance
        gamma_final = 0.01  # Final gamma for refined exploitation
        gamma_decay = (gamma_final / gamma_initial) ** (1 / self.budget)  # Exponential decay
        elite_count = 5  # Increased elite count for diversity
        mutation_strength = 0.05  # Moderate mutation strength
        crossover_probability = 0.7  # Adjusted crossover probability
        tunneling_frequency = 0.5  # Adjusted tunneling frequency to avoid excessive randomness

        # Initialize population within bounds
        population = np.random.uniform(-5.0, 5.0, (population_size, self.dim))
        fitness = np.array([func(ind) for ind in population])
        evaluations_left = self.budget - population_size

        while evaluations_left > 0:
            gamma = gamma_initial * (gamma_decay ** (self.budget - evaluations_left))

            # Elite selection
            elite_indices = np.argsort(fitness)[:elite_count]
            elite_individuals = population[elite_indices]
            new_population = [population[i] for i in elite_indices]
            new_fitness = [fitness[i] for i in elite_indices]

            # Reproduction: crossover and mutation
            while len(new_population) < population_size:
                parent1_idx, parent2_idx = np.random.choice(elite_indices, 2, replace=False)
                parent1, parent2 = population[parent1_idx], population[parent2_idx]

                # Crossover
                if np.random.random() < crossover_probability:
                    crossover_point = np.random.randint(1, self.dim)
                    offspring = np.concatenate([parent1[:crossover_point], parent2[crossover_point:]])
                else:
                    offspring = np.array(parent1)

                # Mutation
                mutation = np.random.normal(0, mutation_strength, self.dim)
                offspring += mutation
                offspring = np.clip(offspring, -5.0, 5.0)

                # Quantum tunneling
                if np.random.rand() < tunneling_frequency:
                    tunnel_point = np.random.uniform(-5.0, 5.0, self.dim)
                    offspring = gamma * offspring + (1 - gamma) * tunnel_point

                offspring_fitness = func(offspring)
                evaluations_left -= 1

                if evaluations_left <= 0:
                    break

                new_population.append(offspring)
                new_fitness.append(offspring_fitness)

                if offspring_fitness < self.f_opt:
                    self.f_opt = offspring_fitness
                    self.x_opt = offspring

            population = np.array(new_population)
            fitness = np.array(new_fitness)

        return self.f_opt, self.x_opt
