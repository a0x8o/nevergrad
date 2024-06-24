import numpy as np


class EnhancedFireworkSwarmOptimization:
    def __init__(self, budget=10000, n_fireworks=50, n_sparks=10):
        self.budget = budget
        self.n_fireworks = n_fireworks
        self.n_sparks = n_sparks
        self.dim = 5
        self.bounds = (-5.0, 5.0)
        self.f_opt = np.inf
        self.x_opt = None

    def initialize_fireworks(self):
        return np.random.uniform(self.bounds[0], self.bounds[1], (self.n_fireworks, self.dim))

    def explode_firework(self, firework, alpha):
        sparks = np.random.uniform(firework - alpha, firework + alpha, (self.n_sparks, self.dim))
        return sparks

    def clip_to_bounds(self, x):
        return np.clip(x, self.bounds[0], self.bounds[1])

    def evolve_fireworks(self, fireworks, func):
        for i in range(self.n_fireworks):
            alpha = np.random.uniform(0.1, 0.9)  # Adaptive alpha
            sparks = self.explode_firework(fireworks[i], alpha)

            for _ in range(self.n_sparks):
                idx1, idx2, idx3 = np.random.choice(self.n_fireworks, 3, replace=False)
                mutant = self.clip_to_bounds(
                    fireworks[idx1] + np.random.uniform(0.1, 0.9) * (fireworks[idx2] - fireworks[idx3])
                )

                trial = np.where(np.random.rand(self.dim) < 0.9, mutant, fireworks[i])
                if func(trial) < func(fireworks[i]):
                    fireworks[i] = trial

        return fireworks

    def update_best_firework(self, fireworks, func):
        best_idx = np.argmin([func(firework) for firework in fireworks])
        if func(fireworks[best_idx]) < self.f_opt:
            self.f_opt = func(fireworks[best_idx])
            self.x_opt = fireworks[best_idx]

    def __call__(self, func):
        fireworks = self.initialize_fireworks()

        for _ in range(self.budget):
            fireworks = self.evolve_fireworks(fireworks, func)

        self.update_best_firework(fireworks, func)

        return self.f_opt, self.x_opt
