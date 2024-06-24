import numpy as np


class EnhancedHarmonyTabuSearchV4:
    def __init__(
        self,
        budget=1000,
        num_harmonies=50,
        num_dimensions=5,
        bandwidth=0.1,
        tabu_tenure=5,
        pitch_adjustment_rate=0.5,
    ):
        self.budget = budget
        self.num_harmonies = num_harmonies
        self.num_dimensions = num_dimensions
        self.bandwidth = bandwidth
        self.tabu_tenure = tabu_tenure
        self.pitch_adjustment_rate = pitch_adjustment_rate
        self.tabu_list = []

    def initialize_positions(self, bounds):
        return np.random.uniform(bounds.lb, bounds.ub, size=(self.num_harmonies, self.num_dimensions))

    def generate_new_solution(self, harmony_memory, best_solution, bounds):
        new_solution = np.zeros_like(harmony_memory[0])
        for i in range(self.num_dimensions):
            if np.random.rand() < self.pitch_adjustment_rate:
                indexes = np.random.choice(range(self.num_harmonies), size=2, replace=False)
                new_solution[i] = np.mean(harmony_memory[indexes, i])
            else:
                new_solution[i] = np.random.uniform(bounds.lb[i], bounds.ub[i])

        new_solution = np.clip(new_solution, bounds.lb, bounds.ub)
        return new_solution

    def update_tabu_list(self, new_solution_str):
        self.tabu_list.append(new_solution_str)
        if len(self.tabu_list) > self.tabu_tenure:
            self.tabu_list.pop(0)

    def evaluate_harmony(self, harmony, func):
        return func(harmony)

    def harmonize(self, func, harmony_memory):
        harmony_scores = [self.evaluate_harmony(harmony, func) for harmony in harmony_memory]
        best_index = np.argmin(harmony_scores)
        return harmony_memory[best_index], harmony_scores[best_index]

    def update_memory(self, harmony_memory, new_solution, func):
        worst_index = np.argmax([func(harmony) for harmony in harmony_memory])
        if func(new_solution) < func(harmony_memory[worst_index]):
            harmony_memory[worst_index] = new_solution

    def __call__(self, func):
        self.f_opt = np.inf
        self.x_opt = None
        bounds = func.bounds

        harmony_memory = self.initialize_positions(bounds)

        for i in range(self.budget):
            new_solution = self.generate_new_solution(harmony_memory, self.x_opt, bounds)
            new_solution_str = ",".join(map(str, new_solution))
            if new_solution_str not in self.tabu_list:
                self.update_memory(harmony_memory, new_solution, func)
                self.update_tabu_list(new_solution_str)

            best_harmony, best_score = self.harmonize(func, harmony_memory)
            if best_score < self.f_opt:
                self.f_opt = best_score
                self.x_opt = best_harmony

        return self.f_opt, self.x_opt
