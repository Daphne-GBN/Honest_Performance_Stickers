import json
import csv
from loader import make_graph
from classical_runner import run_sa, run_pt
from qaoa_depth_runner import optimize_qaoa
from optimizer_runner import run_optimizer
from noise_runner import optimize_noisy_qaoa
from results_store import ResultsStore


def test_all_runners_integrate_with_results_store(tmp_path):
    graph = make_graph(
        3,
        [(0, 1, 1), (1, 2, 1), (0, 2, 1)],
        name="triangle_integration",
    )

    store = ResultsStore(output_dir=tmp_path)

    common = {
        "seed": 42,
        "num_sweeps": 50,
        "num_reads": 2,
        "num_replicas": 2,
        "min_temp": 0.1,
        "max_temp": 5.0,
    }

    # 1. Simulated Annealing
    sa = run_sa(graph, **common)
    sa_record = store.record_experiment(
        graph, sa, solver="SA"
    )

    # 2. Parallel Tempering
    pt = run_pt(graph, **common)
    pt_record = store.record_experiment(
        graph, pt, solver="PT"
    )

    # 3. Original noiseless QAOA
    qaoa = optimize_qaoa(
        graph, p=1, seed=42, maxiter=10
    )
    qaoa_record = store.record_experiment(
        graph, qaoa, solver="QAOA"
    )

    # 4. Optimizer comparison
    optimizer = run_optimizer(
        graph,
        p=1,
        optimizer="COBYLA",
        seed=42,
        max_evaluations=10,
    )
    optimizer_record = store.record_experiment(
        graph, optimizer, solver="QAOA-Optimizer"
    )

    # 5. Noisy QAOA
    noisy = optimize_noisy_qaoa(
        graph,
        p=1,
        noise_probability=0.005,
        optimizer="COBYLA",
        seed=42,
        max_evaluations=5,
    )
    noisy_record = store.record_experiment(
        graph,
        noisy,
        solver="Noisy-QAOA",
    )

    records = [
        sa_record,
        pt_record,
        qaoa_record,
        optimizer_record,
        noisy_record,
    ]

    assert len(records) == 5

    for record in records:
        assert record["instance"] == "triangle_integration"
        assert record["exact_optimum"] == 2.0

    assert sa_record["best_cut"] is not None
    assert pt_record["best_cut"] is not None
    assert qaoa_record["expected_cut"] is not None
    assert optimizer_record["expected_cut"] is not None
    assert noisy_record["expected_cut"] is not None
    assert noisy_record["noise_probability"] == 0.005

    assert store.csv_path.exists()
    assert store.jsonl_path.exists()
    assert optimizer_record["best_cut"] is None
    assert optimizer_record["expected_cut"] is not None
    assert optimizer_record["approximation_ratio"] is None

    assert noisy_record["best_cut"] is None
    assert noisy_record["expected_cut"] is not None

def test_repeated_run_summary_is_saved_to_csv_and_jsonl(tmp_path):
    graph = make_graph(
        3,
        [(0, 1, 1), (1, 2, 1), (0, 2, 1)],
        name="tts_integration",
    )

    store = ResultsStore(output_dir=tmp_path)

    summary = store.summarize_repeated_runs(
        cut_values=[2, 1, 2, 2],
        exact_optimum=2,
        runtime_per_run_seconds=0.5,
    )

    result = {
        "best_cut": 2,
        "expected_cut": 1.8,
    }

    record = store.record_experiment(
        graph,
        result,
        solver="SA",
        repeated_run_summary=summary,
    )

    assert record["run_count"] == 4
    assert record["success_probability"] == 0.75
    assert record["repetitions_to_99"] == 4
    assert record["time_to_solution_99_seconds"] == 2.0

    with store.jsonl_path.open(encoding="utf-8") as file:
        saved_json = json.loads(file.readline())

    assert saved_json["run_count"] == 4
    assert saved_json["time_to_solution_99_seconds"] == 2.0

    with store.csv_path.open(
        newline="",
        encoding="utf-8",
    ) as file:
        saved_csv = next(csv.DictReader(file))

    assert int(saved_csv["run_count"]) == 4
    assert float(saved_csv["time_to_solution_99_seconds"]) == 2.0
