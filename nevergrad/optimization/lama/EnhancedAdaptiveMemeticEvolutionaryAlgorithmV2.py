import numpy as np


class EnhancedAdaptiveMemeticEvolutionaryAlgorithmV2:
    def __init__(self, budget, population_size=50):
        self.budget = budget
        self.population_size = population_size

    def gradient_estimation(self, func, x, h=1e-6):
        grad = np.zeros_like(x)
        for i in range(len(x)):
            x1 = np.copy(x)
            x2 = np.copy(x)
            x1[i] += h
            x2[i] -= h
            grad[i] = (func(x1) - func(x2)) / (2 * h)
        return grad

    def evolutionary_step(self, func, pop, scores, crossover_rate):
        new_pop = np.copy(pop)
        new_scores = np.copy(scores)
        for i in range(self.population_size):
            idxs = [idx for idx in range(self.population_size) if idx != i]
            a, b, c = pop[np.random.choice(idxs, 3, replace=False)]
            F = 0.5 + np.random.rand() * 0.3
            mutant = np.clip(a + F * (b - c), -5.0, 5.0)
            cross_points = np.random.rand(len(mutant)) < crossover_rate
            if not np.any(cross_points):
                cross_points[np.random.randint(0, len(mutant))] = True
            trial = np.where(cross_points, mutant, pop[i])
            f = func(trial)
            if f < scores[i]:
                new_scores[i] = f
                new_pop[i] = trial
        return new_pop, new_scores

    def local_search(self, func, x, score, learning_rate):
        grad = self.gradient_estimation(func, x)
        candidate = np.clip(x - learning_rate * grad, -5.0, 5.0)
        f = func(candidate)
        if f < score:
            return candidate, f
        return x, score

    def adaptive_parameters(self, iteration, max_iterations):
        crossover_rate = 0.9 - 0.5 * ((iteration / max_iterations) ** 0.5)
        learning_rate = 0.01 * ((1 - iteration / max_iterations) ** 0.5)
        memetic_probability = 0.5 * (1 + np.cos(iteration / max_iterations * np.pi))
        return crossover_rate, learning_rate, memetic_probability

    def hybrid_step(self, func, pop, scores, crossover_rate, learning_rate, memetic_probability):
        new_pop, new_scores = self.evolutionary_step(func, pop, scores, crossover_rate)
        for i in range(self.population_size):
            if np.random.rand() < memetic_probability:
                new_pop[i], new_scores[i] = self.local_search(func, new_pop[i], new_scores[i], learning_rate)
        return new_pop, new_scores

    def __call__(self, func):
        np.random.seed(0)
        dim = 5
        lower_bound = -5.0
        upper_bound = 5.0

        # Initialize population
        pop = np.random.uniform(lower_bound, upper_bound, (self.population_size, dim))
        scores = np.array([func(ind) for ind in pop])

        # Global best initialization
        best_idx = np.argmin(scores)
        global_best_position = pop[best_idx]
        global_best_score = scores[best_idx]

        evaluations = self.population_size
        max_iterations = self.budget // self.population_size

        iteration = 0
        while evaluations < self.budget:
            crossover_rate, learning_rate, memetic_probability = self.adaptive_parameters(
                iteration, max_iterations
            )

            # Perform hybrid step
            pop, scores = self.hybrid_step(
                func, pop, scores, crossover_rate, learning_rate, memetic_probability
            )
            evaluations += self.population_size

            # Update global best from population
            best_idx = np.argmin(scores)
            if scores[best_idx] < global_best_score:
                global_best_score = scores[best_idx]
                global_best_position = pop[best_idx]

            iteration += 1

        self.f_opt = global_best_score
        self.x_opt = global_best_position
        return self.f_opt, self.x_opt
