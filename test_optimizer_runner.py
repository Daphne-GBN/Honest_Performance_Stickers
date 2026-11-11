import numpy as np
from loader import load_gset
from metrics import exact_maxcut
from optimizer_runner import run_optimizer, OPTIMIZERS
def main():
    graph = load_gset(
        "maxcut_instances/instances/cycle_n10_s0.txt"
    )

    optimum = exact_maxcut(graph)["optimum"]
    all_results = []

    print("=" * 75)
    print("STAGE 5 - QAOA OPTIMIZER COMPARISON")
    print("=" * 75)
    print(f"Graph: {graph.name}")
    print(f"Vertices: {graph.n}")
    print(f"Edges: {graph.m}")
    print(f"Exact maximum cut: {optimum}")
    print("Evaluation budget per optimizer: 100")
    print("QAOA depths: p=1, p=2, p=3")

    for p in (1, 2, 3):
        print("\n" + "=" * 75)
        print(f"QAOA DEPTH p={p}")
        print("=" * 75)

        for optimizer in OPTIMIZERS:
            print(f"\nRunning {optimizer} at p={p}...")

            result = run_optimizer(
                graph=graph,
                p=p,
                optimizer=optimizer,
                seed=42,
                max_evaluations=100
            )
                        # Validate optimizer output
            assert len(result["best_gammas"]) == p
            assert len(result["best_betas"]) == p

            assert result["objective_evaluations"] <= 100
            assert result["validation_evaluations"] == 1

            assert np.isfinite(result["best_expected_cut"])
            assert 0 <= result["best_expected_cut"] <= optimum

            assert np.isclose(
                result["best_expected_cut"],
                result["validation_expected_cut"],
                atol=1e-5
            )

            assert all(
                0 <= gamma <= np.pi
                for gamma in result["best_gammas"]
            )

            assert all(
                0 <= beta <= np.pi / 2
                for beta in result["best_betas"]
            )

            print("Result validation: PASSED")

            result["approximation_ratio"] = (
                result["best_expected_cut"] / optimum
            )

            all_results.append(result)

            print(
                f"Expected cut: "
                f"{result['best_expected_cut']:.6f}"
            )
            print(
                f"Approximation ratio: "
                f"{result['approximation_ratio']:.4f}"
            )
            print(
                f"Objective evaluations: "
                f"{result['objective_evaluations']}"
            )
            print(
                f"Runtime: "
                f"{result['wall_runtime_seconds']:.3f} seconds"
            )
            print(
                f"Optimizer success: "
                f"{result['optimizer_success']}"
            )
            print(f"Message: {result['optimizer_message']}")

    print("\n" + "=" * 90)
    print("FINAL COMPARISON")
    print("=" * 90)

    print(
        f"{'Depth':<8}"
        f"{'Optimizer':<15}"
        f"{'Expected Cut':<16}"
        f"{'Ratio':<10}"
        f"{'Evaluations':<14}"
        f"{'Runtime (s)':<14}"
        f"{'Success'}"
    )

    for result in all_results:
        print(
            f"{result['p']:<8}"
            f"{result['optimizer']:<15}"
            f"{result['best_expected_cut']:<16.6f}"
            f"{result['approximation_ratio']:<10.4f}"
            f"{result['objective_evaluations']:<14}"
            f"{result['wall_runtime_seconds']:<14.3f}"
            f"{result['optimizer_success']}"
        )

    print("\nTotal experiments:", len(all_results))
    print("Stage 5 depth comparison completed.")


if __name__ == "__main__":
    main()
