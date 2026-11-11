
import csv
import json

from loader import make_graph
from results_store import ResultsStore


def create_triangle():
    return make_graph(
        n=3,
        edges=[(0, 1), (1, 2), (0, 2)],
        name="triangle_test",
    )


def test_build_classical_record(tmp_path):
    graph = create_triangle()
    store = ResultsStore(output_dir=tmp_path)

    result = {
        "best_cut": 2.0,
        "mean_cut": 1.8,
        "wall_runtime_seconds": 0.5,
    }

    record = store.build_record(
        graph,
        result,
        solver="SA",
        seed=42,
    )

    assert record["best_cut"] == 2.0
    assert record["exact_optimum"] == 2.0
    assert record["approximation_ratio"] == 1.0
    assert record["solver"] == "SA"


def test_build_qaoa_record(tmp_path):
    graph = create_triangle()
    store = ResultsStore(output_dir=tmp_path)

    result = {
        "p": 1,
        "expected_cut": 1.8,
        "most_probable_cut": 2.0,
        "function_evaluations": 50,
        "optimizer_success": True,
    }

    record = store.build_record(
        graph,
        result,
        solver="QAOA",
        optimizer="COBYLA",
        seed=42,
    )

    assert record["best_cut"] == 2.0
    assert record["expected_cut"] == 1.8
    assert record["p"] == 1
    assert record["function_evaluations"] == 50


def test_save_csv_and_jsonl(tmp_path):
    graph = create_triangle()
    store = ResultsStore(output_dir=tmp_path)

    result = {
        "best_cut": 2.0,
        "wall_runtime_seconds": 0.5,
    }

    record = store.record_experiment(
        graph,
        result,
        solver="SA",
    )

    assert store.csv_path.exists()
    assert store.jsonl_path.exists()

    with store.csv_path.open(
        newline="",
        encoding="utf-8",
    ) as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 1
    assert rows[0]["solver"] == "SA"

    with store.jsonl_path.open(
        encoding="utf-8",
    ) as file:
        saved = json.loads(file.readline())

    assert saved["best_cut"] == 2.0
    assert saved["instance"] == "triangle_test"


def test_incremental_saving(tmp_path):
    graph = create_triangle()
    store = ResultsStore(output_dir=tmp_path)

    for seed in [42, 43, 44]:
        store.record_experiment(
            graph,
            {"best_cut": 2.0},
            solver="SA",
            seed=seed,
        )

    with store.jsonl_path.open(encoding="utf-8") as file:
        records = [json.loads(line) for line in file]

    assert len(records) == 3
    assert [r["seed"] for r in records] == [42, 43, 44]


def test_exact_optimum_can_be_unavailable(tmp_path):
    graph = create_triangle()

    store = ResultsStore(
        output_dir=tmp_path,
        exact_max_nodes=2,
    )

    record = store.build_record(
        graph,
        {"best_cut": 2.0},
        solver="SA",
    )

    assert record["exact_optimum"] is None
    assert record["approximation_ratio"] is None


def test_missing_metrics_are_preserved(tmp_path):
    graph = create_triangle()
    store = ResultsStore(output_dir=tmp_path)

    record = store.build_record(
        graph,
        {},
        solver="QAOA",
    )

    assert record["best_cut"] is None
    assert record["expected_cut"] is None
    assert record["runtime_seconds"] is None
    assert record["success_probability"] is None
   
def test_repeated_run_metrics_and_tts(tmp_path):
    store = ResultsStore(output_dir=tmp_path)

    summary = store.summarize_repeated_runs(
        cut_values=[2, 1, 2, 2],
        exact_optimum=2,
        runtime_per_run_seconds=0.5,
    )

    assert summary["runs"] == 4
    assert summary["successes"] == 3
    assert summary["success_probability"] == 0.75
    assert summary["repetitions_to_99"] == 4
    assert summary["time_to_solution_99_seconds"] == 2.0


def test_tts_unavailable_when_success_probability_is_zero(tmp_path):
    store = ResultsStore(output_dir=tmp_path)

    summary = store.summarize_repeated_runs(
        cut_values=[0, 1, 0],
        exact_optimum=2,
        runtime_per_run_seconds=0.5,
    )

    assert summary["success_probability"] == 0.0
    assert summary["repetitions_to_99"] is None
    assert summary["time_to_solution_99_seconds"] is None