
import time
import numpy as np
from scipy.optimize import minimize

from hybridq.noise.utils import add_depolarizing_noise
from hybridq.dm.circuit.simulation import simulate as dm_simulate

from qaoa_depth_runner import build_qaoa_circuit
from optimizer_runner import parameter_bounds, clip_parameters
from loader import cut_value


def run_noisy_qaoa(graph, gammas, betas, noise_probability):
    """Run QAOA with gate-local depolarizing noise."""

    if not 0.0 <= noise_probability <= 1.0:
        raise ValueError("Noise probability must be between 0 and 1.")

    circuit = build_qaoa_circuit(graph, gammas, betas)

    noisy_circuit = add_depolarizing_noise(
        circuit,
        noise_probability,
        where="after"
    )

    rho = np.asarray(
        dm_simulate(noisy_circuit, initial_state="0" * graph.n)
    ).reshape(2 ** graph.n, 2 ** graph.n)

    probabilities = np.real(np.diag(rho))

    if not np.all(np.isfinite(probabilities)):
        raise ValueError("Invalid density-matrix probabilities.")

    if not np.isclose(np.trace(rho), 1.0, atol=1e-5):
        raise ValueError("Density matrix trace is not 1.")

    if not np.isclose(probabilities.sum(), 1.0, atol=1e-5):
        raise ValueError("Probabilities do not sum to 1.")

    if np.min(probabilities) < -1e-6:
        raise ValueError("Negative measurement probability detected.")

    return rho, np.maximum(probabilities, 0.0)


def calculate_noisy_expected_cut(graph, probabilities):
    """Calculate expected MaxCut from density-matrix probabilities."""

    return float(sum(
        probability * cut_value(
            graph,
            format(index, f"0{graph.n}b")
        )
        for index, probability in enumerate(probabilities)
    ))


def optimize_noisy_qaoa(
    graph,
    p,
    noise_probability,
    optimizer="COBYLA",
    seed=42,
    max_evaluations=100
):
    """Optimize noisy QAOA using COBYLA or SPSA."""

    optimizer = optimizer.upper()

    if optimizer not in ("COBYLA", "SPSA"):
        raise ValueError("Choose COBYLA or SPSA.")

    if p not in (1, 2, 3):
        raise ValueError("p must be 1, 2, or 3.")

    if max_evaluations < 2:
        raise ValueError("Evaluation budget must be at least 2.")

    rng = np.random.default_rng(seed)
    bounds = parameter_bounds(p)

    parameters = np.concatenate([
        np.full(p, 0.5),
        np.full(p, 0.25)
    ])

    evaluation_count = 0
    best_parameters = parameters.copy()
    best_value = float("-inf")

    def evaluate(values):
        nonlocal evaluation_count, best_parameters, best_value

        if evaluation_count >= max_evaluations:
            raise RuntimeError("Evaluation budget exhausted.")

        values = clip_parameters(values, bounds)

        _, probabilities = run_noisy_qaoa(
            graph,
            values[:p],
            values[p:],
            noise_probability
        )

        expected_cut = calculate_noisy_expected_cut(
            graph, probabilities
        )

        evaluation_count += 1

        if expected_cut > best_value:
            best_value = expected_cut
            best_parameters = values.copy()

        return -expected_cut

    start = time.perf_counter()
    success = None
    message = ""

    try:
        if optimizer == "COBYLA":
            result = minimize(
                evaluate,
                parameters,
                method="COBYLA",
                bounds=bounds,
                options={
                    "maxiter": max_evaluations,
                    "rhobeg": 0.2,
                    "tol": 1e-3
                }
            )
            success = bool(result.success)
            message = str(result.message)

        else:
            iterations = max_evaluations // 2
            a, c = 0.08, 0.12

            for k in range(iterations):
                delta = rng.choice([-1.0, 1.0], size=2 * p)

                plus = clip_parameters(
                    parameters + c * delta, bounds
                )
                minus = clip_parameters(
                    parameters - c * delta, bounds
                )

                loss_plus = evaluate(plus)
                loss_minus = evaluate(minus)

                gradient = (
                    (loss_plus - loss_minus) / (2 * c * delta)
                )

                parameters = clip_parameters(
                    parameters - a * gradient / ((k + 1) ** 0.602),
                    bounds
                )

            message = "SPSA completed; convergence not independently certified."

    except RuntimeError as error:
        message = str(error)

    optimization_runtime = time.perf_counter() - start

    # Independent validation of the best parameters.
    validation_start = time.perf_counter()

    rho, probabilities = run_noisy_qaoa(
        graph,
        best_parameters[:p],
        best_parameters[p:],
        noise_probability
    )

    expected_cut = calculate_noisy_expected_cut(
        graph, probabilities
    )

    validation_runtime = time.perf_counter() - validation_start

    return {
        "optimizer": optimizer,
        "p": p,
        "noise_probability": noise_probability,
        "seed": seed,
        "gammas": best_parameters[:p].tolist(),
        "betas": best_parameters[p:].tolist(),
        "expected_cut": expected_cut,
        "probability_sum": float(probabilities.sum()),
        "density_matrix_trace": float(np.real(np.trace(rho))),
        "function_evaluations": evaluation_count,
        "max_evaluations": max_evaluations,
        "optimization_runtime": optimization_runtime,
        "validation_runtime": validation_runtime,
        "optimizer_success": success,
        "optimizer_message": message
    }
