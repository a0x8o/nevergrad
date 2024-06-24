import numpy as np


class QuantumStochasticGradientOptimizer:
    def __init__(self, budget, dim=5, learning_rate=0.1, momentum=0.9, quantum_boost=False):
        self.budget = budget
        self.dim = dim
        self.learning_rate = learning_rate
        self.momentum = momentum
        self.quantum_boost = quantum_boost
        self.lower_bound = -5.0
        self.upper_bound = 5.0

    def initialize(self):
        self.position = np.random.uniform(self.lower_bound, self.upper_bound, self.dim)
        self.velocity = np.zeros(self.dim)
        self.best_position = np.copy(self.position)
        self.best_fitness = np.inf

    def evaluate(self, func, position):
        return func(position)

    def update_position(self):
        self.velocity = self.momentum * self.velocity + self.learning_rate * np.random.normal(0, 1, self.dim)
        self.position += self.velocity
        self.position = np.clip(self.position, self.lower_bound, self.upper_bound)

    def quantum_influence(self):
        if self.quantum_boost:
            self.position += np.random.normal(0, 0.1 * (self.upper_bound - self.lower_bound), self.dim)
            self.position = np.clip(self.position, self.lower_bound, self.upper_bound)

    def __call__(self, func):
        self.initialize()

        for _ in range(self.budget):
            self.update_position()
            self.quantum_influence()
            fitness = self.evaluate(func, self.position)

            if fitness < self.best_fitness:
                self.best_fitness = fitness
                self.best_position = np.copy(self.position)

        return self.best_fitness, self.best_position
