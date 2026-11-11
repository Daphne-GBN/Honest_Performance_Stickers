
import csv
from noise_runner import optimize_noisy_qaoa
from loader import make_graph

graph = make_graph(
    3,
    [(0, 1, 1), (1, 2, 1), (0, 2, 1)],
    name="triangle_noise_pilot"
)

noise_rates = [0.0, 0.001, 0.005, 0.02]
depths = [1, 2]
optimizers = ["COBYLA", "SPSA"]
seeds = [42, 43, 44]

results = []

for noise in noise_rates:
    for p in depths:
        for optimizer in optimizers:
            for seed in seeds:

                print(
                    f"Running noise={noise}, p={p}, "
                    f"optimizer={optimizer}, seed={seed}"
                )

                result = optimize_noisy_qaoa(
                    graph=graph,
                    p=p,
                    noise_probability=noise,
                    optimizer=optimizer,
                    seed=seed,
                    max_evaluations=10
                )

                results.append(result)

with open("noise_pilot_results.csv", "w", newline="") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=results[0].keys()
    )
    writer.writeheader()
    writer.writerows(results)

print("\nPilot completed.")
print("Total experiments:", len(results))
print("Saved: noise_pilot_results.csv")
