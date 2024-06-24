import numpy as np


class EnhancedAdaptiveMemoryGradientAnnealingWithExplorationBoost:
    def __init__(self, budget=10000):
        self.budget = budget
        self.dim = None

    def __call__(self, func):
        self.dim = len(func.bounds.lb)
        self.f_opt = np.Inf
        self.x_opt = None
        evaluations = 0

        # Annealing properties
        T_initial = 1.0
        T_min = 1e-5
        alpha_initial = 0.97
        beta_initial = 1.5

        # Initial solution
        x_current = np.random.uniform(func.bounds.lb, func.bounds.ub)
        f_current = func(x_current)
        evaluations += 1

        # Memory for storing best solutions
        memory_size = 20  # Larger memory size for more diversity
        memory = np.zeros((memory_size, self.dim))
        memory_scores = np.full(memory_size, np.Inf)
        memory[0] = x_current
        memory_scores[0] = f_current

        # Initial settings
        T = T_initial
        alpha = alpha_initial
        beta = beta_initial

        # Define dynamic phases
        phase1 = self.budget // 3  # Exploration phase
        phase2 = 2 * self.budget // 3  # Exploitation phase

        while evaluations < self.budget and T > T_min:
            for _ in range(memory_size):
                if np.random.rand() < 0.5:
                    # Disturbance around current best memory solution
                    x_candidate = memory[np.argmin(memory_scores)] + T * np.random.randn(self.dim)
                else:
                    # Random memory selection
                    x_candidate = memory[np.random.randint(memory_size)] + T * np.random.randn(self.dim)

                x_candidate = np.clip(x_candidate, func.bounds.lb, func.bounds.ub)
                f_candidate = func(x_candidate)
                evaluations += 1

                if f_candidate < f_current or np.exp(beta * (f_current - f_candidate) / T) > np.random.rand():
                    x_current = x_candidate
                    f_current = f_candidate

                    # Update memory with better solutions
                    worst_idx = np.argmax(memory_scores)
                    if f_current < memory_scores[worst_idx]:
                        memory[worst_idx] = x_current
                        memory_scores[worst_idx] = f_current

                    if f_current < self.f_opt:
                        self.f_opt = f_current
                        self.x_opt = x_current

            T *= alpha

            # Dynamic adjustment of beta and alpha for better exploration-exploitation balance
            if evaluations < phase1:
                beta = 2.5  # Higher exploration phase
                alpha = 0.99  # Slower cooling for thorough exploration
            elif evaluations < phase2:
                beta = 1.5  # Balanced phase
                alpha = 0.97  # Standard cooling rate
            else:
                beta = 3.0  # Higher acceptance for local search refinement
                alpha = 0.90  # Faster cooling for final convergence

            # Gradient-based local search refinement occasionally
            if evaluations % (self.budget // 8) == 0 and evaluations < self.budget:
                x_best_memory = memory[np.argmin(memory_scores)]
                x_best_memory = self._local_refinement(func, x_best_memory)
                f_best_memory = func(x_best_memory)
                evaluations += 1
                if f_best_memory < self.f_opt:
                    self.f_opt = f_best_memory
                    self.x_opt = x_best_memory

            # Dimensional adjustment to escape local minima and diversify search
            if evaluations % (self.budget // 6) == 0 and evaluations < self.budget:
                x_best_memory = memory[np.argmin(memory_scores)]
                x_best_memory = self._dimensional_adjustment(func, x_best_memory)
                f_best_memory = func(x_best_memory)
                evaluations += 1
                if f_best_memory < self.f_opt:
                    self.f_opt = f_best_memory
                    self.x_opt = x_best_memory

            # Periodic exploration boost
            if evaluations % (self.budget // 4) == 0:
                for _ in range(memory_size // 2):  # Half the memory size for exploration boost
                    x_candidate = np.random.uniform(func.bounds.lb, func.bounds.ub)
                    f_candidate = func(x_candidate)
                    evaluations += 1
                    if f_candidate < self.f_opt:
                        self.f_opt = f_candidate
                        self.x_opt = x_candidate

                    # Update memory with better solutions
                    worst_idx = np.argmax(memory_scores)
                    if f_candidate < memory_scores[worst_idx]:
                        memory[worst_idx] = x_candidate
                        memory_scores[worst_idx] = f_candidate

        return self.f_opt, self.x_opt

    def _local_refinement(self, func, x, iters=50, step_size=0.01):
        for _ in range(iters):
            gradient = self._approximate_gradient(func, x)
            x -= step_size * gradient  # Gradient descent step
            x = np.clip(x, func.bounds.lb, func.bounds.ub)
        return x

    def _approximate_gradient(self, func, x, epsilon=1e-8):
        grad = np.zeros_like(x)
        fx = func(x)
        for i in range(self.dim):
            x_eps = np.copy(x)
            x_eps[i] += epsilon
            grad[i] = (func(x_eps) - fx) / epsilon
        return grad

    def _dimensional_adjustment(self, func, x, step_factor=0.1):
        new_x = np.copy(x)
        for i in range(self.dim):
            new_x[i] += step_factor * (np.random.uniform(-1, 1) * (func.bounds.ub[i] - func.bounds.lb[i]))
        new_x = np.clip(new_x, func.bounds.lb, func.bounds.ub)
        return new_x
