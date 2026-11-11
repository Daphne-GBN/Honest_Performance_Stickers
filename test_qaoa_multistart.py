
import numpy as np
from scipy.optimize import minimize
from loader import load_gset
from metrics import exact_maxcut
from qaoa_depth_runner import (
    run_qaoa,
    calculate_expected_cut
)
# Load graph
graph = load_gset(
    "maxcut_instances/instances/cycle_n10_s0.txt",
    name="cycle_n10_s0"
)
known_optimum = exact_maxcut(graph)["optimum"]
print("=" * 60)
print("QAOA MULTI-START OPTIMIZATION")
print("=" * 60)
print("Graph:", graph.name)
print("Vertices:", graph.n)
print("Edges:", graph.m)
print("Exact maximum cut:", known_optimum)
rng = np.random.default_rng(42)
# Experiment configuration
depths = (2, 3)
num_starts = 5
maxiter = 500
all_results = []
for p in depths:
    print("\n" + "=" * 50)
    print(f"QAOA DEPTH p={p}")
    print("=" * 50)
    best_result = None
    for start in range(num_starts):
        # Random initial gamma and beta values
        initial_gammas = rng.uniform(0.1, np.pi - 0.1, p)
        initial_betas = rng.uniform(0.05, np.pi / 2 - 0.05, p)
        initial_parameters = np.concatenate(
            [initial_gammas, initial_betas]
        )
        def objective(parameters):
            gammas = parameters[:p]
            betas = parameters[p:]
            statevector = run_qaoa(
                graph,
                gammas,
                betas
            )
            return -calculate_expected_cut(
                graph,
                statevector
            )
        # Apply parameter bounds
        bounds = (
            [(0.0, np.pi)] * p
            + [(0.0, np.pi / 2)] * p
        )
        result = minimize(
            objective,
            x0=initial_parameters,
            method="COBYLA",
            bounds=bounds,
            options={
                "maxiter": maxiter,
                "rhobeg": 0.2,
                "tol": 1e-3,
                "disp": False
            }
        )
        expected_cut = -float(result.fun)
        print(
            f"Start {start + 1}: "
            f"Expected cut={expected_cut:.6f}, "
            f"Success={result.success}, "
            f"Evaluations={result.nfev}"
        )
        current = {
            "p": p,
            "start": start + 1,
            "expected_cut": expected_cut,
            "success": bool(result.success),
            "evaluations": int(result.nfev),
            "parameters": result.x.tolist()
        }
        all_results.append(current)
        if (
            best_result is None
            or expected_cut > best_result["expected_cut"]
        ):
            best_result = current
    print("\nBEST RESULT FOR p =", p)
    print("Expected cut:", best_result["expected_cut"])
    print("Parameters:", best_result["parameters"])
    print("Optimizer success:", best_result["success"])
    print("Function evaluations:", best_result["evaluations"])
# Final summary
print("\n" + "=" * 60)
print("MULTI-START SUMMARY")
print("=" * 60)
for p in depths:
    depth_results = [
        item for item in all_results
        if item["p"] == p
    ]
    best = max(
        depth_results,
        key=lambda item: item["expected_cut"]
    )
    print(
        f"p={p}: Best expected cut="
        f"{best['expected_cut']:.6f}, "
        f"Optimizer success={best['success']}"
    )
print("\nMULTI-START EXPERIMENT COMPLETED")