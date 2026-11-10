
import time
import numpy as np
import numba

from pysa.sa import Solver
from loader import to_pysa_qubo, cut_value


@numba.njit
def seed_numba_rng(seed):
    np.random.seed(seed)


def validate_result(graph, state, reported_energy, tolerance=1e-5):
    state = np.asarray(state, dtype=float)

    if state.shape != (graph.n,):
        raise ValueError("Invalid state length.")

    if not np.all(np.isin(state, [0.0, 1.0])):
        raise ValueError("State must contain only 0 and 1.")

    bitstring = "".join(str(int(bit)) for bit in state)
    actual_cut = cut_value(graph, bitstring)
    actual_energy = -actual_cut

    return {
        "state": bitstring,
        "cut": float(actual_cut),
        "energy": float(actual_energy),
        "reported_energy": float(reported_energy),
        "energy_valid": bool(
            np.isclose(actual_energy, float(reported_energy), atol=tolerance)
        )
    }


def run_classical(
    graph,
    solver_type="sa",
    seed=42,
    num_sweeps=4000,
    num_reads=5,
    num_replicas=8,
    min_temp=0.1,
    max_temp=5.0
):
    if solver_type not in ("sa", "pt"):
        raise ValueError("solver_type must be 'sa' or 'pt'.")

    if num_sweeps <= 0 or num_reads <= 0 or num_replicas <= 0:
        raise ValueError("Sweeps, reads and replicas must be positive.")

    if min_temp <= 0 or max_temp <= min_temp:
        raise ValueError("Invalid temperature range.")

    qubo = np.asarray(to_pysa_qubo(graph), dtype=np.float32)

    solver = Solver(
        problem=qubo,
        problem_type="qubo",
        float_type="float32"
    )

    use_pt = solver_type == "pt"

    def seed_all(value):
        np.random.seed(value)
        seed_numba_rng(int(value))

    def execute(sweeps, reads):
        return solver.metropolis_update(
            num_sweeps=sweeps,
            num_reads=reads,
            num_replicas=num_replicas,
            min_temp=min_temp,
            max_temp=max_temp,
            parallel=False,
            use_pt=use_pt,
            recompute_energy=True,
            return_dataframe=True,
            verbose=False
        )

    # Warm-up: exclude first-time compilation from benchmark timing.
    seed_all(seed)
    warmup_start = time.perf_counter()
    execute(sweeps=1, reads=1)
    warmup_runtime = time.perf_counter() - warmup_start

    # Reset seeds so the measured run starts reproducibly.
    seed_all(seed)

    wall_start = time.perf_counter()
    raw_results = execute(
        sweeps=num_sweeps,
        reads=num_reads
    )
    wall_runtime = time.perf_counter() - wall_start

    results = []
    replica_results = []

    total_init_time = 0
    total_solver_runtime = 0

    for read_index, (_, row) in enumerate(raw_results.iterrows()):

        total_init_time += int(row["init_time (us)"])
        total_solver_runtime += int(row["runtime (us)"])

        states = np.asarray(row["states"], dtype=float)
        energies = np.asarray(row["energies"], dtype=float)

        if states.ndim == 1:
            states = states.reshape(1, -1)

        if energies.ndim == 0:
            energies = energies.reshape(1)

        if len(states) != len(energies):
            raise ValueError("Replica states and energies do not match.")

        for replica_index, (state, energy) in enumerate(
            zip(states, energies)
        ):
            replica = validate_result(graph, state, energy)

            replica.update({
                "read_index": read_index,
                "replica_index": replica_index,
                "seed": seed,
                "solver": solver_type
            })

            if not replica["energy_valid"]:
                raise ValueError("Replica energy validation failed.")

            replica_results.append(replica)

        best = validate_result(
            graph,
            row["best_state"],
            row["best_energy"]
        )

        best.update({
            "read_index": read_index,
            "seed": seed,
            "solver": solver_type
        })

        if not best["energy_valid"]:
            raise ValueError("Best-state energy validation failed.")

        results.append(best)

    if not results or not replica_results:
        raise ValueError("PySA returned no results.")

    best_result = max(results, key=lambda item: item["cut"])

    return {
        "solver": solver_type,
        "seed": seed,
        "parameters": {
            "num_sweeps": num_sweeps,
            "num_reads": num_reads,
            "num_replicas": num_replicas,
            "min_temp": min_temp,
            "max_temp": max_temp
        },
        "warmup_runtime_seconds": warmup_runtime,
        "wall_runtime_seconds": wall_runtime,
        "initialization_time_seconds": total_init_time / 1e6,
        "solver_runtime_seconds": total_solver_runtime / 1e6,
        "results": results,
        "replica_results": replica_results,
        "best_result": best_result,
        "best_cut": best_result["cut"],
        "mean_cut": float(np.mean([r["cut"] for r in results])),
        "total_replicas_validated": len(replica_results),
        "validation_passed": True
    }


def run_sa(graph, **kwargs):
    return run_classical(graph, solver_type="sa", **kwargs)


def run_pt(graph, **kwargs):
    return run_classical(graph, solver_type="pt", **kwargs)
