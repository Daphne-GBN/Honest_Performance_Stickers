
import time
import numpy as np
from scipy.optimize import minimize

from qaoa_depth_runner import run_qaoa, calculate_expected_cut


OPTIMIZERS = ("COBYLA", "NELDER-MEAD", "SPSA", "ADAM")


def parameter_bounds(p):
    """Return bounds for gamma and beta parameters."""
    return (
        [(0.0, np.pi)] * p
        + [(0.0, np.pi / 2)] * p
    )


def clip_parameters(parameters, bounds):
    """Keep all parameters within their valid ranges."""
    return np.array([
        np.clip(value, lower, upper)
        for value, (lower, upper) in zip(parameters, bounds)
    ], dtype=float)


def run_optimizer(
    graph,
    p,
    optimizer="COBYLA",
    seed=42,
    max_evaluations=200,
    initial_parameters=None
):
    """
    Optimize QAOA parameters using COBYLA, Nelder-Mead,
    SPSA, or Adam.

    All optimizers share the same objective-evaluation budget.
    Final validation is counted separately.
    """

    optimizer = optimizer.upper().replace("_", "-")

    if optimizer not in OPTIMIZERS:
        raise ValueError(
            f"Unsupported optimizer. Choose from {OPTIMIZERS}."
        )

    if p not in (1, 2, 3):
        raise ValueError("p must be 1, 2, or 3.")

    if max_evaluations < 2:
        raise ValueError("max_evaluations must be at least 2.")

    rng = np.random.default_rng(seed)
    bounds = parameter_bounds(p)

    if initial_parameters is None:
        initial_parameters = np.concatenate([
            np.full(p, 0.5),
            np.full(p, 0.25)
        ])

    initial_parameters = clip_parameters(
        np.asarray(initial_parameters, dtype=float),
        bounds
    )

    if len(initial_parameters) != 2 * p:
        raise ValueError("Expected exactly 2*p parameters.")

    evaluation_count = 0
    best_parameters = initial_parameters.copy()
    best_value = float("-inf")
    history = []

    def evaluate(parameters):
        nonlocal evaluation_count
        nonlocal best_parameters
        nonlocal best_value

        if evaluation_count >= max_evaluations:
            raise RuntimeError("Evaluation budget exhausted.")

        parameters = clip_parameters(parameters, bounds)

        statevector = run_qaoa(
            graph,
            parameters[:p],
            parameters[p:]
        )

        expected_cut = calculate_expected_cut(
            graph, statevector
        )

        evaluation_count += 1
        history.append(float(expected_cut))

        if expected_cut > best_value:
            best_value = float(expected_cut)
            best_parameters = parameters.copy()

        return -float(expected_cut)

    start_time = time.perf_counter()
    optimizer_success = False
    optimizer_message = ""

    try:
        if optimizer in ("COBYLA", "NELDER-MEAD"):

            method = (
                "COBYLA"
                if optimizer == "COBYLA"
                else "Nelder-Mead"
            )

            result = minimize(
                evaluate,
                x0=initial_parameters,
                method=method,
                bounds=bounds,
                options=(
                    {
                        "maxiter": max_evaluations,
                        "rhobeg": 0.2,
                        "tol": 1e-3,
                        "disp": False
                     }
                    if optimizer == "COBYLA"
                    else {
                        
                        "maxfev": max_evaluations,
                        "xatol": 1e-3,
                        "fatol": 1e-3,
                        "disp": False
                    }
                )  
            )  
            optimizer_success = bool(result.success)
            optimizer_message = str(result.message)

        elif optimizer == "SPSA":

            # Simultaneous Perturbation Stochastic Approximation.
            # Each iteration estimates a gradient using two evaluations.

            parameters = initial_parameters.copy()
            iterations = max_evaluations // 2

            a = 0.08
            c = 0.12
            alpha = 0.602
            gamma = 0.101

            for k in range(iterations):

                ak = a / ((k + 1) ** alpha)
                ck = c / ((k + 1) ** gamma)

                delta = rng.choice(
                    [-1.0, 1.0],
                    size=2 * p
                )

                plus = clip_parameters(
                    parameters + ck * delta,
                    bounds
                )

                minus = clip_parameters(
                    parameters - ck * delta,
                    bounds
                )

                loss_plus = evaluate(plus)
                loss_minus = evaluate(minus)

                gradient = (
                    (loss_plus - loss_minus)
                    / (2.0 * ck * delta)
                )

                parameters = clip_parameters(
                    parameters - ak * gradient,
                    bounds
                )

            optimizer_success = None
            optimizer_message = (
                "SPSA completed its evaluation budget; "
                "convergence was not independently certified."
            )

        elif optimizer == "ADAM":

            # Adam with central finite-difference gradients.

            parameters = initial_parameters.copy()

            learning_rate = 0.025
            beta1 = 0.9
            beta2 = 0.999
            epsilon = 1e-8

            first_moment = np.zeros(2 * p)
            second_moment = np.zeros(2 * p)

            # One base evaluation plus two evaluations per parameter
            # for each numerical gradient.

            gradient_cost = 2 * (2 * p) + 1
            iterations = max(
                1,
                (max_evaluations - 1) // gradient_cost
            )

            for iteration in range(1, iterations + 1):

                current_loss = evaluate(parameters)
                gradient = np.zeros(2 * p)

                step = 1e-3

                for j in range(2 * p):

                    plus = parameters.copy()
                    minus = parameters.copy()

                    plus[j] += step
                    minus[j] -= step

                    plus = clip_parameters(plus, bounds)
                    minus = clip_parameters(minus, bounds)

                    actual_step = plus[j] - minus[j]

                    if actual_step == 0:
                        gradient[j] = 0.0
                        continue

                    loss_plus = evaluate(plus)
                    loss_minus = evaluate(minus)

                    gradient[j] = (
                        loss_plus - loss_minus
                    ) / actual_step

                first_moment = (
                    beta1 * first_moment
                    + (1 - beta1) * gradient
                )

                second_moment = (
                    beta2 * second_moment
                    + (1 - beta2) * (gradient ** 2)
                )

                corrected_first = (
                    first_moment / (1 - beta1 ** iteration)
                )

                corrected_second = (
                    second_moment / (1 - beta2 ** iteration)
                )

                parameters = clip_parameters(
                    parameters
                    - learning_rate * corrected_first
                    / (np.sqrt(corrected_second) + epsilon),
                    bounds
                )

            optimizer_success =  None
            optimizer_message = (
                "Adam completed its numerical-gradient iterations; "
                "convergence was not independently certified."
            )

    except RuntimeError as error:
        optimizer_message = str(error)

    wall_runtime = time.perf_counter() - start_time

    # Validate the best parameters found during optimization.
    validation_start = time.perf_counter()

    best_statevector = run_qaoa(
        graph,
        best_parameters[:p],
        best_parameters[p:]
    )

    validation_expected_cut = calculate_expected_cut(
        graph,
        best_statevector
    )

    validation_runtime = time.perf_counter() - validation_start

    if not np.isclose(
        validation_expected_cut,
        best_value,
        atol=1e-5
    ):
        raise RuntimeError("Final validation did not match best result.")

    return {
        "optimizer": optimizer,
        "p": p,
        "seed": seed,
        "best_gammas": best_parameters[:p].tolist(),
        "best_betas": best_parameters[p:].tolist(),
        "best_expected_cut": float(best_value),
        "validation_expected_cut": float(validation_expected_cut),
        "optimizer_success": optimizer_success,
        "optimizer_message": optimizer_message,
        "objective_evaluations": evaluation_count,
        "validation_evaluations": 1,
        "wall_runtime_seconds": float(wall_runtime),
        "validation_runtime_seconds": float(validation_runtime),
        "history": history
    }
