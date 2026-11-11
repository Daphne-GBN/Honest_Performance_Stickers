
from loader import load_gset
from metrics import exact_maxcut
from qaoa_depth_runner import optimize_qaoa

# Load the 10-node cycle graph
graph = load_gset(
    "maxcut_instances/instances/cycle_n10_s0.txt",
    name="cycle_n10_s0"
)

known_optimum = exact_maxcut(graph)["optimum"]

print("=" * 55)
print("QAOA DEPTH BENCHMARK - 10 NODE CYCLE")
print("=" * 55)

print("Vertices:", graph.n)
print("Edges:", graph.m)
print("Exact maximum cut:", known_optimum)

results = []

# Test all three QAOA depths
for p in (1, 2, 3):
    print("\n" + "=" * 45)
    print(f"RUNNING QAOA p={p}")
    print("=" * 45)

    result = optimize_qaoa(
        graph,
        p=p,
        seed=42,
        maxiter=100
    )

    results.append(result)

    print("Gammas:", result["gammas"])
    print("Betas:", result["betas"])
    print("Expected cut:", result["expected_cut"])
    print("Most probable bitstring:", result["most_probable_bitstring"])
    print("Most probable cut:", result["most_probable_cut"])
    print("Statevector size:", result["statevector_size"])
    print("Probability sum:", result["probability_sum"])
    print("Optimizer success:", result["optimizer_success"])
    print("Function evaluations:", result["function_evaluations"])

# Validate results
print("\n" + "=" * 55)
print("VALIDATION")
print("=" * 55)

for result in results:
    p = result["p"]

    assert len(result["gammas"]) == p
    assert len(result["betas"]) == p
    assert result["statevector_size"] == 2 ** graph.n
    assert abs(result["probability_sum"] - 1.0) < 1e-5
    assert -1e-6 <= result["expected_cut"] <= known_optimum + 1e-5

    print(f"p={p}: PASSED")

print("\n10-NODE QAOA DEPTH BENCHMARK COMPLETED")
