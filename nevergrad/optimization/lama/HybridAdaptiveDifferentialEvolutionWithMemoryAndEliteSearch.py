import numpy as np


class HybridAdaptiveDifferentialEvolutionWithMemoryAndEliteSearch:
    def __init__(self, budget=10000):
        self.budget = budget
        self.dim = 5
        self.pop_size = 50
        self.initial_F = 0.8
        self.initial_CR = 0.9
        self.tau1 = 0.1
        self.tau2 = 0.1
        self.elitism_rate = 0.2  # Fraction of elite individuals to retain
        self.memory_size = 5
        self.memory_F = [self.initial_F] * self.memory_size
        self.memory_CR = [self.initial_CR] * self.memory_size
        self.memory_index = 0
        self.diversity_threshold = 1e-5  # Threshold to restart the population
        self.learning_rate = 0.1  # Learning rate for elite learning

    def initialize_population(self, bounds):
        return np.random.uniform(bounds.lb, bounds.ub, (self.pop_size, self.dim))

    def select_parents(self, population, idx):
        indices = list(range(0, self.pop_size))
        indices.remove(idx)
        idxs = np.random.choice(indices, 3, replace=False)
        return population[idxs]

    def mutate(self, parent1, parent2, parent3, F):
        return np.clip(parent1 + F * (parent2 - parent3), -5.0, 5.0)

    def crossover(self, target, mutant, CR):
        j_rand = np.random.randint(self.dim)
        return np.where(np.random.rand(self.dim) < CR, mutant, target)

    def diversity(self, population):
        return np.mean(np.std(population, axis=0))

    def adapt_parameters(self):
        F = self.memory_F[self.memory_index]
        CR = self.memory_CR[self.memory_index]
        if np.random.rand() < self.tau1:
            F = np.clip(np.random.normal(F, 0.1), 0, 1)
        if np.random.rand() < self.tau2:
            CR = np.clip(np.random.normal(CR, 0.1), 0, 1)
        return F, CR

    def local_search(self, individual, bounds, func):
        best_individual = np.copy(individual)
        best_fitness = func(best_individual)
        for _ in range(5):  # Make a small number of local perturbations
            mutation = np.random.randn(self.dim) * 0.01
            trial = np.clip(individual + mutation, bounds.lb, bounds.ub)
            trial_fitness = func(trial)
            if trial_fitness < best_fitness:
                best_individual = trial
                best_fitness = trial_fitness
        return best_individual, best_fitness

    def elite_learning(self, elite, global_best):
        return np.clip(
            elite + self.learning_rate * np.random.randn(self.dim) * (global_best - elite), -5.0, 5.0
        )

    def restart_population(self, bounds):
        return self.initialize_population(bounds)

    def __call__(self, func):
        self.f_opt = np.inf
        self.x_opt = None
        bounds = func.bounds

        population = self.initialize_population(bounds)
        personal_best_positions = np.copy(population)
        personal_best_scores = np.array([func(ind) for ind in population])
        global_best_position = personal_best_positions[np.argmin(personal_best_scores)]
        global_best_score = np.min(personal_best_scores)
        evaluations = self.pop_size

        while evaluations < self.budget:
            new_population = np.zeros((self.pop_size, self.dim))
            fitness = np.zeros(self.pop_size)

            for i in range(self.pop_size):
                parents = self.select_parents(population, i)
                parent1, parent2, parent3 = parents
                F, CR = self.adapt_parameters()
                mutant = self.mutate(parent1, parent2, parent3, F)
                trial = self.crossover(population[i], mutant, CR)

                trial_fitness = func(trial)
                evaluations += 1

                if trial_fitness < personal_best_scores[i]:
                    personal_best_positions[i] = trial
                    personal_best_scores[i] = trial_fitness

                if personal_best_scores[i] < global_best_score:
                    global_best_position = personal_best_positions[i]
                    global_best_score = personal_best_scores[i]

                new_population[i] = trial
                fitness[i] = trial_fitness

                if evaluations >= self.budget:
                    break

            # Perform local search on the top fraction of the population
            elite_indices = np.argsort(fitness)[: int(self.elitism_rate * self.pop_size)]
            for i in elite_indices:
                new_population[i], fitness[i] = self.local_search(new_population[i], bounds, func)
                evaluations += 5

            # Apply elitism: retain the top performing individuals
            elite_population = new_population[elite_indices]
            non_elite_indices = np.argsort(fitness)[int(self.elitism_rate * self.pop_size) :]
            for i in non_elite_indices:
                learned_trial = self.elite_learning(new_population[i], global_best_position)
                learned_fitness = func(learned_trial)
                evaluations += 1

                if learned_fitness < fitness[i]:
                    new_population[i] = learned_trial
                    fitness[i] = learned_fitness
                    if learned_fitness < self.f_opt:
                        self.f_opt = learned_fitness
                        self.x_opt = learned_trial

                if evaluations >= self.budget:
                    break

            # Check for diversity and restart if too low
            if self.diversity(new_population) < self.diversity_threshold:
                new_population = self.restart_population(bounds)
                personal_best_positions = np.copy(new_population)
                personal_best_scores = np.array([func(ind) for ind in new_population])
                global_best_position = personal_best_positions[np.argmin(personal_best_scores)]
                global_best_score = np.min(personal_best_scores)
                evaluations += self.pop_size

            # Update population with new candidates
            population = np.copy(new_population)

            # Update memory for F and CR
            self.memory_F[self.memory_index] = F
            self.memory_CR[self.memory_index] = CR
            self.memory_index = (self.memory_index + 1) % self.memory_size

        return self.f_opt, self.x_opt
