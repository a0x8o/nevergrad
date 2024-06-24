import numpy as np


class EnhancedMetaPopulationAdaptiveGradientSearch:
    def __init__(
        self,
        budget,
        population_size=50,
        elite_fraction=0.2,
        initial_sigma=0.5,
        c_c=0.1,
        c_s=0.3,
        c_1=0.2,
        c_mu=0.3,
        damps=1.0,
        learning_rate=0.001,
        gradient_steps=10,
        meta_population_size=3,
    ):
        self.budget = budget
        self.population_size = population_size
        self.elite_fraction = elite_fraction
        self.initial_sigma = initial_sigma
        self.c_c = c_c  # cumulation for C
        self.c_s = c_s  # cumulation for sigma control
        self.c_1 = c_1  # learning rate for rank-one update
        self.c_mu = c_mu  # learning rate for rank-mu update
        self.damps = damps  # damping for step-size
        self.learning_rate = learning_rate  # learning rate for gradient-based local search
        self.gradient_steps = gradient_steps  # number of gradient descent steps
        self.meta_population_size = meta_population_size  # number of meta-populations

    def __adaptive_covariance_matrix_adaptation(self, func, pop, mean, C, sigma):
        n_samples = self.population_size
        dim = pop.shape[1]

        new_pop = np.zeros_like(pop)
        new_scores = np.zeros(n_samples)

        for i in range(n_samples):
            z = np.random.randn(dim)
            try:
                y = np.dot(np.linalg.cholesky(C), z)
            except np.linalg.LinAlgError:
                y = np.dot(np.linalg.cholesky(C + 1e-8 * np.eye(dim)), z)
            candidate = np.clip(mean + sigma * y, -5.0, 5.0)
            new_pop[i] = candidate
            new_scores[i] = func(candidate)

        return new_pop, new_scores

    def __gradient_local_search(self, func, x):
        eps = 1e-8
        for _ in range(self.gradient_steps):
            grad = np.zeros_like(x)
            fx = func(x)

            for i in range(len(x)):
                x_eps = np.copy(x)
                x_eps[i] += eps
                grad[i] = (func(x_eps) - fx) / eps

            x -= self.learning_rate * grad
            x = np.clip(x, -5.0, 5.0)

        return x

    def __hierarchical_selection(self, pop, scores):
        elite_count = int(self.population_size * self.elite_fraction)
        elite_idx = np.argsort(scores)[:elite_count]
        elite_pop = pop[elite_idx]

        diverse_count = int(self.population_size * (1 - self.elite_fraction))
        diverse_idx = np.argsort(scores)[-diverse_count:]
        diverse_pop = pop[diverse_idx]

        return elite_pop, diverse_pop

    def __call__(self, func):
        np.random.seed(0)
        dim = 5
        lower_bound = -5.0
        upper_bound = 5.0

        # Initialize meta-populations
        meta_populations = []
        for _ in range(self.meta_population_size):
            pop = np.random.uniform(lower_bound, upper_bound, (self.population_size, dim))
            scores = np.array([func(ind) for ind in pop])
            meta_populations.append((pop, scores))

        evaluations = self.population_size * self.meta_population_size
        max_iterations = self.budget // (self.population_size * self.meta_population_size)

        # Initialize global best
        global_best_score = np.inf
        global_best_position = None

        for pop, scores in meta_populations:
            best_idx = np.argmin(scores)
            if scores[best_idx] < global_best_score:
                global_best_score = scores[best_idx]
                global_best_position = pop[best_idx]

        for iteration in range(max_iterations):
            for idx, (pop, scores) in enumerate(meta_populations):
                # Initialize mean, covariance matrix, and sigma
                mean = np.mean(pop, axis=0)
                C = np.cov(pop.T)
                sigma = self.initial_sigma

                # Perform adaptive covariance matrix adaptation step
                pop, scores = self.__adaptive_covariance_matrix_adaptation(func, pop, mean, C, sigma)

                # Update global best
                best_idx = np.argmin(scores)
                if scores[best_idx] < global_best_score:
                    global_best_score = scores[best_idx]
                    global_best_position = pop[best_idx]

                # Apply gradient-based local search to elite individuals in the population
                elite_pop, diverse_pop = self.__hierarchical_selection(pop, scores)
                for i in range(len(elite_pop)):
                    elite_pop[i] = self.__gradient_local_search(func, elite_pop[i])
                    scores[i] = func(elite_pop[i])

                # Update global best after local search
                best_idx = np.argmin(scores)
                if scores[best_idx] < global_best_score:
                    global_best_score = scores[best_idx]
                    global_best_position = pop[best_idx]

                # Hierarchical selection
                elite_pop, diverse_pop = self.__hierarchical_selection(pop, scores)

                # Update mean, covariance matrix, and sigma
                mean_new = np.mean(elite_pop, axis=0)

                if iteration == 0:
                    dim = elite_pop.shape[1]
                    pc = np.zeros(dim)
                    ps = np.zeros(dim)
                    chi_n = np.sqrt(dim) * (1 - 1 / (4.0 * dim) + 1 / (21.0 * dim**2))

                ps = (1 - self.c_s) * ps + np.sqrt(self.c_s * (2 - self.c_s)) * (mean_new - mean) / sigma
                hsig = (
                    np.linalg.norm(ps)
                    / np.sqrt(1 - (1 - self.c_s) ** (2 * evaluations / self.population_size))
                ) < (1.4 + 2 / (dim + 1))
                pc = (1 - self.c_c) * pc + hsig * np.sqrt(self.c_c * (2 - self.c_c)) * (
                    mean_new - mean
                ) / sigma

                artmp = (elite_pop - mean) / sigma
                C = (
                    (1 - self.c_1 - self.c_mu) * C
                    + self.c_1 * np.outer(pc, pc)
                    + self.c_mu * np.dot(artmp.T, artmp) / elite_pop.shape[0]
                )
                sigma *= np.exp((np.linalg.norm(ps) / chi_n - 1) * self.damps)

                mean = mean_new

                evaluations += self.population_size

                if evaluations >= self.budget:
                    break

            if evaluations >= self.budget:
                break

        self.f_opt = global_best_score
        self.x_opt = global_best_position
        return self.f_opt, self.x_opt
