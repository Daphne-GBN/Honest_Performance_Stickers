
from loader import make_graph
from metrics import exact_maxcut
from qaoa_depth_runner import optimize_qaoa

# Create a 3-node triangle graph
graph = make_graph(
    3,
    [(0, 1, 1), (1, 2, 1), (0, 2, 1)],
    name="triangle_test"
)

# Calculate the exact maximum cut
known_optimum = exact_maxcut(graph)

print("GRAPH")
print("Vertices:", graph.n)
print("Edges:", graph.m)
print("Known maximum cut:", known_optimum["optimum"])

all_results = []

# Test QAOA depths p=1, p=2 and p=3
for p in (1, 2, 3):
    print("\n" + "=" * 45)
    print(f"QAOA WITH p = {p}")
    print("=" * 45)

    result = optimize_qaoa(
        graph,
        p=p,
        seed=42,
        maxiter=100
    )

    all_results.append(result)

    print("Gammas:", result["gammas"])
    print("Betas:", result["betas"])
    print("Expected cut:", result["expected_cut"])
    print("Most probable bitstring:", result["most_probable_bitstring"])
    print("Most probable cut:", result["most_probable_cut"])
    print("Statevector size:", result["statevector_size"])
    print("Probability sum:", result["probability_sum"])
    print("Optimizer success:", result["optimizer_success"])
    print("Function evaluations:", result["function_evaluations"])

# Validate all three QAOA depths
print("\n" + "=" * 45)
print("VALIDATION")
print("=" * 45)

for result in all_results:
    assert len(result["gammas"]) == result["p"]
    assert len(result["betas"]) == result["p"]
    assert result["statevector_size"] == 2 ** graph.n
    assert abs(result["probability_sum"] - 1.0) < 1e-5
    assert result["expected_cut"] >= -1e-6
    assert result["expected_cut"] <= known_optimum["optimum"] + 1e-5

    print(f"p={result['p']}: PASSED")

print("\nQAOA DEPTH TEST COMPLETED")
