import numpy as np


class QuantumTunnelingOptimizerV14:
    def __init__(self, budget=10000):
        self.budget = budget
        self.dim = 5  # Fixed dimensionality

    def __call__(self, func):
        self.f_opt = np.inf
        self.x_opt = None

        # Hyperparameters refinement for enhanced performance
        population_size = 500  # Scaled-down population for more iterations per individual
        gamma = 0.08  # Starting gamma slightly increased for broader early exploration
        gamma_min = 0.00001  # Minimum gamma remains same for fine-tuning in late stages
        gamma_decay = 0.99  # Slower gamma decay to sustain exploration capabilities longer
        elite_count = 50  # Reduced elitism count, focusing on top 10% of the population
        mutation_strength = 0.01  # Increased mutation strength for broader search
        crossover_probability = 0.85  # Slightly reduced to promote more diverse mutations
        tunneling_frequency = 0.50  # Increased tunneling frequency for enhanced exploration

        # Initialize population uniformly within bounds
        population = np.random.uniform(-5.0, 5.0, (population_size, self.dim))
        fitness = np.array([func(ind) for ind in population])
        evaluations_left = self.budget - population_size

        while evaluations_left > 0:
            # Update gamma according to decay schedule
            gamma = max(gamma * gamma_decay, gamma_min)

            # Elitism: retain the best performing individuals
            elite_indices = np.argsort(fitness)[:elite_count]
            elite_individuals = population[elite_indices]
            new_population = [population[i] for i in elite_indices]
            new_fitness = [fitness[i] for i in elite_indices]

            # Breed new individuals via crossover and mutation
            while len(new_population) < population_size:
                parent1_idx, parent2_idx = np.random.choice(elite_indices, 2, replace=False)
                parent1, parent2 = population[parent1_idx], population[parent2_idx]

                # Crossover
                if np.random.random() < crossover_probability:
                    crossover_point = np.random.randint(1, self.dim)
                    offspring = np.concatenate([parent1[:crossover_point], parent2[crossover_point:]])
                else:
                    offspring = np.array(parent1)  # No crossover, clone parent

                # Mutation
                mutation = np.random.normal(0, mutation_strength, self.dim)
                offspring += mutation
                offspring = np.clip(offspring, -5.0, 5.0)  # Ensure offspring remain within bounds

                # Quantum tunneling effect
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
