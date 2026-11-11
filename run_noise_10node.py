
import csv
from noise_runner import optimize_noisy_qaoa
from loader import load_graph

graph_files = [
    "instances/benchmark/er_n10_p25_s5021.txt",
    "instances/benchmark/er_n10_p50_s5026.txt"
]

noise_rates = [0.0, 0.005, 0.02]
depths = [1, 2]
optimizers = ["COBYLA", "SPSA"]
seeds = [42, 43, 44]

results = []

for graph_file in graph_files:
    graph = load_graph(graph_file)

    print(f"\nGraph: {graph.name}")
    print(f"Nodes: {graph.n}, Edges: {len(graph.edges)}")

    for noise in noise_rates:
        for p in depths:
            for optimizer in optimizers:
                for seed in seeds:

                    print(
                        f"noise={noise}, p={p}, "
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

                    result["graph"] = graph.name
                    result["nodes"] = graph.n
                    result["edges"] = len(graph.edges)

                    results.append(result)

                    # Save incrementally so completed experiments survive interruption.
                    with open(
                        "noise_10node_results.csv",
                        "w",
                        newline=""
                    ) as file:
                        writer = csv.DictWriter(
                            file,
                            fieldnames=results[0].keys()
                        )
                        writer.writeheader()
                        writer.writerows(results)

print("\n10-node pilot completed.")
print("Total experiments:", len(results))
print("Saved: noise_10node_results.csv")
