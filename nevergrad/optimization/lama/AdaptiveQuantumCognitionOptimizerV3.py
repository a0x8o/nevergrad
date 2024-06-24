import numpy as np


class AdaptiveQuantumCognitionOptimizerV3:
    def __init__(
        self,
        budget=10000,
        population_size=100,
        inertia_weight=0.7,
        cognitive_coefficient=1.5,
        social_coefficient=1.5,
        inertia_decay=0.99,
        quantum_jump_rate=0.2,
        quantum_scale=0.05,
        adaptive_scale_factor=0.1,
    ):
        self.budget = budget
        self.population_size = population_size
        self.dim = 5  # Dimensionality of the problem
        self.lb, self.ub = -5.0, 5.0  # Bounds of the search space
        self.inertia_weight = inertia_weight
        self.cognitive_coefficient = cognitive_coefficient
        self.social_coefficient = social_coefficient
        self.inertia_decay = inertia_decay
        self.quantum_jump_rate = quantum_jump_rate
        self.quantum_scale = quantum_scale
        self.adaptive_scale_factor = adaptive_scale_factor

    def __call__(self, func):
        # Initialize particle positions and velocities
        particles = np.random.uniform(self.lb, self.ub, (self.population_size, self.dim))
        velocities = np.zeros_like(particles)
        personal_bests = particles.copy()
        personal_best_scores = np.array([func(p) for p in particles])
        global_best = personal_bests[np.argmin(personal_best_scores)]
        global_best_score = min(personal_best_scores)

        evaluations = self.population_size

        while evaluations < self.budget:
            for i in range(self.population_size):
                # Quantum jump with adaptive scale handling
                if np.random.rand() < self.quantum_jump_rate:
                    # Adjust quantum scale dynamically based on the global best score
                    quantum_deviation = np.random.normal(
                        0,
                        max(
                            0.0001,
                            self.quantum_scale
                            * (1 + self.adaptive_scale_factor * np.log(1 + abs(global_best_score))),
                        ),
                        self.dim,
                    )
                    particles[i] = global_best + quantum_deviation
                    particles[i] = np.clip(particles[i], self.lb, self.ub)
                else:
                    # Standard PSO update with inertia, cognitive, and social components
                    r1, r2 = np.random.rand(2)
                    velocities[i] = (
                        self.inertia_weight * velocities[i]
                        + self.cognitive_coefficient * r1 * (personal_bests[i] - particles[i])
                        + self.social_coefficient * r2 * (global_best - particles[i])
                    )
                    particles[i] += velocities[i]
                    particles[i] = np.clip(particles[i], self.lb, self.ub)

                score = func(particles[i])
                evaluations += 1

                if score < personal_best_scores[i]:
                    personal_bests[i] = particles[i]
                    personal_best_scores[i] = score

                    if score < global_best_score:
                        global_best = particles[i]
                        global_best_score = score

            # Decay inertia weight to promote convergence
            self.inertia_weight *= self.inertia_decay

            if evaluations >= self.budget:
                break

        return global_best_score, global_best
