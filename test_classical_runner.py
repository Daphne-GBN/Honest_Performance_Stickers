
from loader import make_graph
from classical_runner import run_sa, run_pt


graph = make_graph(
    3,
    [(0, 1, 1), (1, 2, 1), (0, 2, 1)],
    name="triangle_test"
)

print("GRAPH")
print("Vertices:", graph.n)
print("Edges:", graph.m)
print("Known maximum cut: 2")


def display_results(name, result):
    print("\n" + "=" * 45)
    print(name)
    print("=" * 45)

    print("Best cut:", result["best_cut"])
    print("Mean cut:", result["mean_cut"])
    print("Warm-up runtime:", result["warmup_runtime_seconds"])
    print("Wall runtime:", result["wall_runtime_seconds"])
    print("Initialization time:", result["initialization_time_seconds"])
    print("Solver runtime:", result["solver_runtime_seconds"])
    print("Validation:", result["validation_passed"])
    print("Total replicas validated:", result["total_replicas_validated"])

    for item in result["results"]:
        print(item)


parameters = {
    "seed": 42,
    "num_sweeps": 100,
    "num_reads": 5,
    "num_replicas": 4,
    "min_temp": 0.1,
    "max_temp": 5.0
}


# Run Simulated Annealing.
sa_result = run_sa(graph, **parameters)
display_results("SIMULATED ANNEALING", sa_result)


# Run Parallel Tempering.
pt_result = run_pt(graph, **parameters)
display_results("PARALLEL TEMPERING", pt_result)


# Reproducibility checks.
print("\n" + "=" * 45)
print("REPRODUCIBILITY TESTS")
print("=" * 45)

sa_repeat = run_sa(graph, **parameters)
pt_repeat = run_pt(graph, **parameters)

sa_states = [r["state"] for r in sa_result["results"]]
sa_repeat_states = [r["state"] for r in sa_repeat["results"]]

pt_states = [r["state"] for r in pt_result["results"]]
pt_repeat_states = [r["state"] for r in pt_repeat["results"]]

sa_identical = sa_states == sa_repeat_states
pt_identical = pt_states == pt_repeat_states

print("SA first run:", sa_states)
print("SA repeated run:", sa_repeat_states)
print("SA reproducible:", sa_identical)

print("PT first run:", pt_states)
print("PT repeated run:", pt_repeat_states)
print("PT reproducible:", pt_identical)

if not sa_identical or not pt_identical:
    raise AssertionError("Reproducibility test failed.")

print("\nCLASSICAL RUNNER TEST COMPLETED")