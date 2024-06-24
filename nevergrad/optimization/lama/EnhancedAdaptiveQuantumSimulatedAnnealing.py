import numpy as np


class EnhancedAdaptiveQuantumSimulatedAnnealing:
    def __init__(
        self,
        budget=10000,
        initial_temp=1.0,
        cooling_rate=0.999,
        explore_ratio=0.1,
        damp_ratio=0.9,
        perturb_factor=0.01,
    ):
        self.budget = budget
        self.dim = 5
        self.temp = initial_temp
        self.cooling_rate = cooling_rate
        self.explore_ratio = explore_ratio
        self.damp_ratio = damp_ratio
        self.perturb_factor = perturb_factor
        self.success_count = 0
        self.failure_count = 0

    def _quantum_step(self, x):
        explore_range = self.explore_ratio * (5.0 - (-5.0))
        return x + np.random.uniform(-explore_range, explore_range, size=self.dim)

    def _acceptance_probability(self, candidate_f, current_f):
        return np.exp((current_f - candidate_f) / self.temp)

    def _perturb_solution(self, x):
        return x + np.random.normal(0, self.perturb_factor, size=self.dim)

    def __call__(self, func):
        self.f_opt = np.Inf
        self.x_opt = None
        current_x = np.random.uniform(-5.0, 5.0, size=self.dim)
        current_f = func(current_x)
        step = 0

        for i in range(self.budget):
            candidate_x = self._quantum_step(current_x)
            candidate_x = np.clip(candidate_x, -5.0, 5.0)
            candidate_f = func(candidate_x)

            if candidate_f < current_f or np.random.rand() < self._acceptance_probability(
                candidate_f, current_f
            ):
                current_x = candidate_x
                current_f = candidate_f
                self.success_count += 1
            else:
                self.failure_count += 1

            current_x = self._perturb_solution(current_x)
            current_x = np.clip(current_x, -5.0, 5.0)
            current_f = func(current_x)

            if current_f < self.f_opt:
                self.f_opt = current_f
                self.x_opt = current_x

            self.temp *= self.cooling_rate
            self.explore_ratio *= self.damp_ratio

            if step % 100 == 0:
                success_rate = self.success_count / (self.success_count + self.failure_count)
                if success_rate < 0.2:
                    self.perturb_factor *= 1.2
                elif success_rate > 0.6:
                    self.perturb_factor *= 0.8

            step += 1

        return self.f_opt, self.x_opt
