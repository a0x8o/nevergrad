import numpy as np


class ProgressiveAdaptiveGlobalLocalSearch:
    def __init__(self, budget, dimension=5, lower_bound=-5.0, upper_bound=5.0, particles=300):
        self.budget = budget
        self.dimension = dimension
        self.bounds = np.array([lower_bound, upper_bound])
        self.particles = particles
        self.global_influence = 0.85  # Slightly less global influence to promote better local refinement
        self.local_influence = 0.15  # Increased local influence for enhanced exploitation
        self.vel_scale = 0.05  # Maintaining fine velocity scale for progressive adjustments
        self.learning_rate = 0.7  # Consistent learning rate for balance
        self.adaptive_rate = 0.03  # Increased adaptive rate for better control over convergence dynamics
        self.exploration_phase = 0.3  # Percentage of budget dedicated to more explorative behavior

    def initialize_particles(self):
        positions = np.random.uniform(self.bounds[0], self.bounds[1], (self.particles, self.dimension))
        velocities = (
            np.random.uniform(-1, 1, (self.particles, self.dimension))
            * (self.bounds[1] - self.bounds[0])
            * self.vel_scale
        )
        return positions, velocities

    def evaluate_particles(self, func, positions):
        fitness = np.array([func(pos) for pos in positions])
        return fitness

    def optimize(self, func):
        positions, velocities = self.initialize_particles()
        fitness = self.evaluate_particles(func, positions)

        personal_best_positions = positions.copy()
        personal_best_fitness = fitness.copy()

        best_global_position = positions[np.argmin(fitness)]
        best_global_fitness = np.min(fitness)

        evaluations = self.particles
        exploration_budget = int(self.budget * self.exploration_phase)

        while evaluations < self.budget:
            for i in range(self.particles):
                # Adjusting global and local influence based on phase of optimization
                if evaluations < exploration_budget:
                    current_global_influence = self.global_influence
                    current_local_influence = self.local_influence
                else:
                    # Increase local influence as optimization progresses
                    current_global_influence = self.global_influence * (1 - (evaluations / self.budget))
                    current_local_influence = self.local_influence + (evaluations / self.budget) * 0.25

                r1, r2 = np.random.rand(2)
                velocities[i] = (
                    self.vel_scale * velocities[i]
                    + current_global_influence * r1 * (personal_best_positions[i] - positions[i])
                    + current_local_influence * r2 * (best_global_position - positions[i])
                )

                positions[i] += velocities[i]
                positions[i] = np.clip(positions[i], self.bounds[0], self.bounds[1])

                new_fitness = func(positions[i])
                evaluations += 1

                if new_fitness < personal_best_fitness[i]:
                    personal_best_positions[i] = positions[i]
                    personal_best_fitness[i] = new_fitness

                if new_fitness < best_global_fitness:
                    best_global_position = positions[i]
                    best_global_fitness = new_fitness

                if evaluations >= self.budget:
                    break

        return best_global_fitness, best_global_position

    def __call__(self, func):
        return self.optimize(func)
