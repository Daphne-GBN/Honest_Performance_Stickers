import numpy as np
from pysa.sa import Solver

qubo = np.array([
    [1, -2],
    [-2, 1]
], dtype=np.float32)

solver = Solver(qubo, "qubo")

log_z, samples, weights = solver.annealed_importance(
    num_temps=10,
    num_samps=20,
    reference_prob="uniform",
    update_strategy="random",
    parallel=False
)

print("QUBO matrix:")
print(qubo)

print("\nNumber of samples:", len(samples))
print("First sample:", samples[0])
print("First sample energy:", solver.get_energy(samples[0]))