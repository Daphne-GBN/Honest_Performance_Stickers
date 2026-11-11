"""
Stage 8: resumable experiment-grid runner.

Run a small smoke grid first:
    python stage8_experiments.py --split benchmark --limit 2 --repeats 1

Run the full noiseless catalogue grid (workstation time may be substantial):
    python stage8_experiments.py --split benchmark --limit 0 --repeats 5

Add the reduced noise study:
    python stage8_experiments.py --split benchmark --limit 2 --repeats 1 --include-noise

The tuning and benchmark splits are deliberately separate. This script does not
perform hyperparameter search; it runs the documented fixed settings and records
them. Do not describe this as completed tuning.
"""
import argparse
import hashlib
import json
import math
import traceback
from pathlib import Path

from classical_runner import run_classical
from loader import load_catalogue
from noise_runner import optimize_noisy_qaoa
from optimizer_runner import OPTIMIZERS, run_optimizer
from results_store import ResultsStore


DEFAULT_NOISE_LEVELS = (0.0, 0.001, 0.005, 0.02)
NOISE_OPTIMIZERS = ("COBYLA", "SPSA")


def parse_int_list(value):
    values = tuple(int(item.strip()) for item in value.split(",") if item.strip())
    if not values or any(item not in (1, 2, 3) for item in values):
        raise argparse.ArgumentTypeError("p values must be selected from 1,2,3")
    return values


def parse_float_list(value):
    try:
        values = tuple(float(item.strip()) for item in value.split(",") if item.strip())
    except ValueError as exc:
        raise argparse.ArgumentTypeError("noise levels must be numbers") from exc
    if not values or any(not math.isfinite(x) or not 0 <= x <= 1 for x in values):
        raise argparse.ArgumentTypeError("noise levels must be between 0 and 1")
    return values


def config_id(config):
    payload = json.dumps(config, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def read_completed(ledger_path):
    completed = set()
    if not ledger_path.exists():
        return completed
    with ledger_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("status") == "completed":
                completed.add(row.get("config_id"))
    return completed


def append_ledger(path, entry):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, allow_nan=False) + "\n")
        handle.flush()


def run_one(graph, config, store, ledger_path, completed):
    cid = config_id(config)
    if cid in completed:
        print(f"SKIP completed: {graph.name} | {config['solver']} | seed={config['seed']}")
        return

    solver = config["solver"]
    seed = config["seed"]
    result = None
    error_text = None
    metadata = {
        "optimizer": config.get("optimizer"),
        "p": config.get("p"),
        "seed": seed,
        "noise_probability": config.get("noise_probability"),
    }
    
    
    try:
        if solver in ("sa", "pt"):
            result = run_classical(
                graph,
                solver_type=solver,
                seed=seed,
                num_sweeps=config["num_sweeps"],
                num_reads=config["num_reads"],
                num_replicas=config["num_replicas"],
                min_temp=config["min_temp"],
                max_temp=config["max_temp"],
            )

        elif solver == "qaoa_noiseless":
            result = run_optimizer(
                graph,
                p=config["p"],
                optimizer=config["optimizer"],
                seed=seed,
                max_evaluations=config["max_evaluations"],
            )

        elif solver == "qaoa_noisy":
            result = optimize_noisy_qaoa(
                graph,
                p=config["p"],
                noise_probability=config["noise_probability"],
                optimizer=config["optimizer"],
                seed=seed,
                max_evaluations=config["noise_max_evaluations"],
            )

        else:
            raise ValueError(f"Unknown solver configuration: {solver}")

        # Explicit numerical validation for QAOA results.
        
        # Explicit numerical validation for QAOA results.
        if solver == "qaoa_noiseless":
            import math

            best_cut = result.get("best_expected_cut")
            validation_cut = result.get("validation_expected_cut")

            valid_values = (
                best_cut is not None
                and validation_cut is not None
                and math.isfinite(float(best_cut))
                and math.isfinite(float(validation_cut))
            )

            valid_range = (
                valid_values
                and -1e-8 <= float(best_cut) <= graph.total_weight + 1e-8
                and -1e-8 <= float(validation_cut) <= graph.total_weight + 1e-8
            )

            consistent = (
                valid_range
                and math.isclose(
                    float(best_cut),
                    float(validation_cut),
                    rel_tol=1e-5,
                    abs_tol=1e-5,
                )
            )

            result["validation_passed"] = bool(consistent)

            if not consistent:
                result["validation_message"] = (
                    "Noiseless QAOA validation failed: "
                    f"best_expected_cut={best_cut}, "
                    f"validation_expected_cut={validation_cut}"
                )

        elif solver == "qaoa_noisy":
            import math

            expected_cut = result.get("expected_cut")
            probability_sum = result.get("probability_sum")
            density_trace = result.get("density_matrix_trace")

            valid_cut = (
                expected_cut is not None
                and math.isfinite(float(expected_cut))
                and -1e-8 <= float(expected_cut) <= graph.total_weight + 1e-8
            )

            valid_probability = (
                probability_sum is not None
                and math.isfinite(float(probability_sum))
                and math.isclose(
                    float(probability_sum), 1.0,
                    rel_tol=1e-5, abs_tol=1e-5
                )
            )

            valid_trace = (
                density_trace is not None
                and math.isfinite(float(density_trace))
                and math.isclose(
                    float(density_trace), 1.0,
                    rel_tol=1e-5, abs_tol=1e-5
                )
            )

            result["validation_passed"] = bool(
                valid_cut and valid_probability and valid_trace
            )

            if not result["validation_passed"]:
                result["validation_message"] = (
                    "Noisy QAOA validation failed: "
                    f"cut={expected_cut}, "
                    f"probability_sum={probability_sum}, "
                    f"density_matrix_trace={density_trace}"
                )

        store.record_experiment(
            graph,
            result,
            solver=solver,
            **metadata,
        )

        append_ledger(ledger_path, {
            "config_id": cid,
            "status": "completed",
            "instance": graph.name,
            **config,
        })
        completed.add(cid)

        print(
            f"OK: {graph.name} | {solver} | "
            f"{config.get('optimizer', '-')} | "
            f"p={config.get('p', '-')} | seed={seed}"
        )

    except Exception as exc:
        error_text = f"{type(exc).__name__}: {exc}"

        try:
            store.record_experiment(
                graph,
                {},
                solver=solver,
                **metadata,
                error=error_text,
            )
        except Exception:
            error_text += (
                " | Failed to persist failure record:\n"
                + traceback.format_exc()
            )

        append_ledger(ledger_path, {
            "config_id": cid,
            "status": "failed",
            "instance": graph.name,
            **config,
            "error": error_text,
        })

        print(f"FAILED: {graph.name} | {solver} | {error_text}")


def build_parser():
    parser = argparse.ArgumentParser(description="Stage 8 resumable MaxCut experiment grid")
    parser.add_argument("--split", choices=("tuning", "benchmark"), default="benchmark")
    parser.add_argument("--limit", type=int, default=2,
                        help="Number of catalogue graphs; 0 means all graphs in selected split")
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--seed-start", type=int, default=100)
    parser.add_argument("--p-values", type=parse_int_list, default=(1, 2, 3))
    parser.add_argument("--max-evaluations", type=int, default=100)
    parser.add_argument("--num-sweeps", type=int, default=1000)
    parser.add_argument("--num-reads", type=int, default=5)
    parser.add_argument("--num-replicas", type=int, default=8)
    parser.add_argument("--include-noise", action="store_true")
    parser.add_argument("--noise-levels", type=parse_float_list, default=DEFAULT_NOISE_LEVELS)
    parser.add_argument("--noise-max-evaluations", type=int, default=20)
    parser.add_argument("--max-qaoa-nodes", type=int, default=20)
    parser.add_argument("--max-noise-nodes", type=int, default=10,
                        help="Density-matrix noise guardrail; keep conservative")
    parser.add_argument("--output-dir", default="results")
    return parser


def main():
    args = build_parser().parse_args()
    if args.limit < 0 or args.repeats < 1:
        raise SystemExit("--limit must be >= 0 and --repeats must be >= 1")
    if args.max_evaluations < 2 or args.noise_max_evaluations < 2:
        raise SystemExit("Evaluation budgets must be at least 2")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    ledger_path = output_dir / "stage8_run_ledger.jsonl"
    completed = read_completed(ledger_path)
    store = ResultsStore(output_dir=output_dir)

    graphs = load_catalogue(split=args.split)
    if args.limit:
        graphs = graphs[:args.limit]

    print("=" * 68)
    print("STAGE 8 EXPERIMENT GRID")
    print(f"Split={args.split} | graphs={len(graphs)} | repeats={args.repeats}")
    print(f"QAOA optimizers={', '.join(OPTIMIZERS)} | p={args.p_values}")
    print(f"Evaluation budget={args.max_evaluations} | noise={args.include_noise}")
    print("Resume ledger:", ledger_path)
    print("=" * 68)

    for graph in graphs:
        for repeat in range(args.repeats):
            seed = args.seed_start + repeat

            for classical_solver in ("sa", "pt"):
                config = {
                    "instance": graph.name, "split": args.split,
                    "solver": classical_solver, "seed": seed,
                    "num_sweeps": args.num_sweeps,
                    "num_reads": args.num_reads,
                    "num_replicas": args.num_replicas,
                    "min_temp": 0.1, "max_temp": 5.0,
                }
                run_one(graph, config, store, ledger_path, completed)

            if graph.n <= args.max_qaoa_nodes:
                for p in args.p_values:
                    for optimizer in OPTIMIZERS:
                        config = {
                            "instance": graph.name, "split": args.split,
                            "solver": "qaoa_noiseless", "optimizer": optimizer,
                            "p": p, "seed": seed,
                            "max_evaluations": args.max_evaluations,
                        }
                        run_one(graph, config, store, ledger_path, completed)
            else:
                print(f"SKIP QAOA guardrail: {graph.name} has {graph.n} nodes "
                      f"(limit {args.max_qaoa_nodes})")

            if args.include_noise:
                if graph.n <= args.max_noise_nodes:
                    for p in args.p_values:
                        for noise in args.noise_levels:
                            for optimizer in NOISE_OPTIMIZERS:
                                config = {
                                    "instance": graph.name, "split": args.split,
                                    "solver": "qaoa_noisy", "optimizer": optimizer,
                                    "p": p, "seed": seed,
                                    "noise_probability": noise,
                                    "noise_max_evaluations": args.noise_max_evaluations,
                                }
                                run_one(graph, config, store, ledger_path, completed)
                else:
                    print(f"SKIP density-matrix noise guardrail: {graph.name} has "
                          f"{graph.n} nodes (limit {args.max_noise_nodes})")

    print("\nStage 8 run finished.")
    print("Raw results:", output_dir / "experiments.jsonl")
    print("CSV results:", output_dir / "experiments.csv")
    print("Resume ledger:", ledger_path)
    print("Completed configurations:", len(completed))
    print("Note: skipped guardrail configurations are not reported as completed.")


if __name__ == "__main__":
    main()
