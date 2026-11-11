
import csv
import json
import math
from pathlib import Path
from datetime import datetime, timezone

from metrics import (
    exact_maxcut,
    approximation_ratio,
    distribution_metrics,
)


CSV_FIELDS = [
    "timestamp",
    "instance",
    "nodes",
    "edges",
    "density",
    "solver",
    "optimizer",
    "p",
    "seed",
    "noise_probability",
    "best_cut",
    "expected_cut",
    "exact_optimum",
    "approximation_ratio",
    "success_probability",
    "run_count",
    "repetitions_to_99",
    "time_to_solution_99_seconds",
    "runtime_seconds",
    "function_evaluations",
    "validation_passed",
    "optimizer_success",
    "simulator",
    "error",
]


def _finite_or_none(value):
    """Convert finite numeric values to floats; preserve missing values."""
    if value is None:
        return None

    value = float(value)
    return value if math.isfinite(value) else None


class ResultsStore:
    """Incremental, shared CSV and JSONL experiment results store."""

    def __init__(
        self,
        output_dir="results",
        exact_max_nodes=22,
        simulator="HybridQ NumPy fallback",
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.csv_path = self.output_dir / "experiments.csv"
        self.jsonl_path = self.output_dir / "experiments.jsonl"

        self.exact_max_nodes = exact_max_nodes
        self.simulator = simulator

    def build_record(
        self,
        graph,
        result,
        solver,
        optimizer=None,
        p=None,
        seed=None,
        noise_probability=None,
        runtime_seconds=None,
        function_evaluations=None,
        success_probability=None,
        validation_passed=None,
        repeated_run_summary=None,
        error=None,
    ):
        """Normalize a runner result into the common schema."""

        best_cut = result.get("best_cut")

        if best_cut is None:
            best_cut = result.get("most_probable_cut")

        expected_cut = result.get("expected_cut")

        if expected_cut is None:
            expected_cut = result.get("best_expected_cut")

        if runtime_seconds is None:
            runtime_seconds = result.get(
                "wall_runtime_seconds",
                result.get(
                    "optimization_runtime",
                    result.get("runtime_seconds"),
                ),
            )

        if function_evaluations is None:
            function_evaluations = result.get(
                "function_evaluations",
                result.get("objective_evaluations"),
            )

        if optimizer is None:
            optimizer = result.get("optimizer")

        if p is None:
            p = result.get("p")

        if seed is None:
            seed = result.get("seed")

        if noise_probability is None:
            noise_probability = result.get("noise_probability")

        if validation_passed is None:
            validation_passed = result.get("validation_passed")

        if validation_passed is None and "probability_sum" in result:
            validation_passed = math.isclose(
                float(result["probability_sum"]),
                1.0,
                abs_tol=1e-3,
            )

        exact_optimum = None

        if graph.n <= self.exact_max_nodes:
            exact_optimum = exact_maxcut(
                graph,
                max_n=self.exact_max_nodes,
            )["optimum"]

        ratio = None

        if best_cut is not None and exact_optimum is not None:
            ratio = approximation_ratio(best_cut, exact_optimum)

        repeated_run_summary = repeated_run_summary or {}

        if success_probability is None:
            success_probability = repeated_run_summary.get(
                "success_probability"
            )

        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "instance": graph.name,
            "nodes": graph.n,
            "edges": graph.m,
            "density": graph.density,
            "solver": solver,
            "optimizer": optimizer,
            "p": p,
            "seed": seed,
            "noise_probability": _finite_or_none(noise_probability),
            "best_cut": _finite_or_none(best_cut),
            "expected_cut": _finite_or_none(expected_cut),
            "exact_optimum": _finite_or_none(exact_optimum),
            "approximation_ratio": _finite_or_none(ratio),
            "success_probability": _finite_or_none(success_probability),
            "run_count": repeated_run_summary.get("runs"),
            "repetitions_to_99": repeated_run_summary.get(
                "repetitions_to_99"
            ),
            "time_to_solution_99_seconds": _finite_or_none(
                repeated_run_summary.get("time_to_solution_99_seconds")
            ),
            "runtime_seconds": _finite_or_none(runtime_seconds),
            "function_evaluations": function_evaluations,
            "validation_passed": validation_passed,
            "optimizer_success": result.get("optimizer_success"),
            "simulator": self.simulator,
            "error": error,
        }

        return record

    def summarize_repeated_runs(
        self,
        cut_values,
        exact_optimum,
        runtime_per_run_seconds=None,
    ):
        """
        Summarize repeated runs and calculate TTS at 99% confidence.

        TTS_99 = repetitions_to_99 * runtime_per_run_seconds.
        """

        summary = distribution_metrics(
            cut_values=cut_values,
            exact_optimum=exact_optimum,
        )

        repetitions = summary["repetitions_to_99"]
        runtime = _finite_or_none(runtime_per_run_seconds)

        tts_99 = None

        if repetitions is not None and runtime is not None and runtime >= 0:
            tts_99 = repetitions * runtime

        summary["time_to_solution_99_seconds"] = tts_99

        return summary

    def save(self, record):
        """Append one record to JSONL and CSV immediately."""

        with self.jsonl_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(record, allow_nan=False) + "\n")

        write_header = (
            not self.csv_path.exists()
            or self.csv_path.stat().st_size == 0
        )

        with self.csv_path.open(
            "a",
            newline="",
            encoding="utf-8",
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=CSV_FIELDS,
                extrasaction="ignore",
            )

            if write_header:
                writer.writeheader()

            writer.writerow(record)

        return record

    def record_experiment(
        self,
        graph,
        result,
        solver,
        **metadata,
    ):
        """Build and immediately save a normalized experiment record."""

        record = self.build_record(
            graph=graph,
            result=result,
            solver=solver,
            **metadata,
        )

        return self.save(record)
