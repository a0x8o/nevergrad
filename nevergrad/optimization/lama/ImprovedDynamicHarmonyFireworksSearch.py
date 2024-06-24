import numpy as np


class ImprovedDynamicHarmonyFireworksSearch:
    def __init__(self, budget=10000, n_fireworks=20, n_sparks=10, alpha=0.1, beta=2, gamma=1, delta=0.2):
        self.budget = budget
        self.n_fireworks = n_fireworks
        self.n_sparks = n_sparks
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.delta = delta
        self.dim = 5
        self.bounds = (-5.0, 5.0)
        self.f_opt = np.inf
        self.x_opt = None

    def initialize_fireworks(self):
        return np.random.uniform(self.bounds[0], self.bounds[1], (self.n_fireworks, self.dim))

    def explode_firework(self, firework):
        sparks = np.random.uniform(firework - self.alpha, firework + self.alpha, (self.n_sparks, self.dim))
        return sparks

    def levy_flight(self, step_size=0.1):
        beta = 1.5
        sigma = (
            np.math.gamma(1 + beta)
            * np.math.sin(np.pi * beta / 2)
            / (np.math.gamma((1 + beta) / 2) * beta * 2 ** ((beta - 1) / 2))
        ) ** (1 / beta)
        u = np.random.normal(0, sigma)
        v = np.random.normal(0, 1)
        step = u / abs(v) ** (1 / beta)
        return step_size * step

    def clip_to_bounds(self, x):
        return np.clip(x, self.bounds[0], self.bounds[1])

    def enhance_fireworks(self, fireworks):
        for i in range(self.n_fireworks):
            for j in range(self.dim):
                fireworks[i][j] += self.levy_flight() * np.random.normal(0, 1)
                fireworks[i][j] = self.clip_to_bounds(fireworks[i][j])
        return fireworks

    def adapt_params(self, iteration):
        alpha = max(0.01, self.alpha / (1 + 0.001 * iteration))  # Adaptive alpha decay
        beta = min(10, self.beta + 0.02)  # Adaptive beta growth
        gamma = max(0.5, self.gamma - 0.001)  # Adaptive gamma decay
        delta = max(0.1, self.delta / (1 + 0.001 * iteration))  # Adaptive delta decay
        return alpha, beta, gamma, delta

    def local_search(self, fireworks, func):
        updated_fireworks = fireworks.copy()

        for i in range(self.n_fireworks):
            trial = fireworks[i] + self.gamma * np.random.normal(0, 1, self.dim)
            trial = self.clip_to_bounds(trial)
            if func(trial) < func(fireworks[i]):
                updated_fireworks[i] = trial

        return updated_fireworks

    def global_search(self, fireworks, func):
        updated_fireworks = fireworks.copy()

        for i in range(self.n_fireworks):
            sparks = self.explode_firework(fireworks[i])
            for j in range(self.n_sparks):
                idx1, idx2 = np.random.choice(np.delete(np.arange(self.n_fireworks), i), 2, replace=False)
                trial = fireworks[i] + self.beta * (fireworks[idx1] - fireworks[idx2])
                trial = self.clip_to_bounds(trial)
                if func(trial) < func(updated_fireworks[i]):
                    updated_fireworks[i] = trial

        return updated_fireworks

    def __call__(self, func):
        fireworks = self.initialize_fireworks()

        for it in range(self.budget):
            self.alpha, self.beta, self.gamma, self.delta = self.adapt_params(it)

            fireworks = self.local_search(fireworks, func)
            fireworks = self.global_search(fireworks, func)

            best_idx = np.argmin([func(firework) for firework in fireworks])
            if func(fireworks[best_idx]) < self.f_opt:
                self.f_opt = func(fireworks[best_idx])
                self.x_opt = fireworks[best_idx]

            fireworks = self.enhance_fireworks(fireworks)

            # Introduce a small delta to encourage local exploration
            for i in range(self.n_fireworks):
                fireworks[i] += self.delta * np.random.normal(0, 1)
                fireworks[i] = self.clip_to_bounds(fireworks[i])

            # Randomly reset some fireworks to encourage exploration
            reset_idx = np.random.choice(self.n_fireworks, int(0.1 * self.n_fireworks), replace=False)
            fireworks[reset_idx] = self.initialize_fireworks()[reset_idx]

        return self.f_opt, self.x_opt
