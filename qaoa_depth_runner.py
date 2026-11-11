
import numpy as np
from scipy.optimize import minimize

from hybridq.gate import Gate
from hybridq.circuit import Circuit
from hybridq.circuit.simulation import simulate

from loader import cut_value


def build_qaoa_circuit(graph, gammas, betas):
    """
    Build a QAOA circuit with p cost layers and p mixer layers.

    gammas: one cost parameter per layer
    betas: one mixer parameter per layer
    """

    gammas = np.asarray(gammas, dtype=float)
    betas = np.asarray(betas, dtype=float)

    if len(gammas) != len(betas):
        raise ValueError("Gamma and beta parameter counts must match.")

    if len(gammas) == 0:
        raise ValueError("At least one QAOA layer is required.")

    gates = []

    # Initial equal superposition.
    for qubit in range(graph.n):
        gates.append(Gate("H", qubits=[qubit]))

    # Apply each cost and mixer layer.
    for gamma, beta in zip(gammas, betas):

        # Cost unitary.
        for u, v, weight in graph.edges:
            gates.append(Gate("CX", qubits=[u, v]))
            gates.append(
                Gate("RZ", qubits=[v], params=[-gamma * weight])
            )
            gates.append(Gate("CX", qubits=[u, v]))

        # Mixer unitary.
        for qubit in range(graph.n):
            gates.append(
                Gate("RX", qubits=[qubit], params=[2 * beta])
            )

    return Circuit(gates)


def run_qaoa(graph, gammas, betas):
    """Simulate QAOA and return its statevector."""

    circuit = build_qaoa_circuit(graph, gammas, betas)

    result = simulate(
        circuit,
        initial_state="0" * graph.n,
        optimize="evolution-einsum",
        simplify=False
    )

    statevector = np.asarray(result).reshape(-1)

    expected_size = 2 ** graph.n

    if len(statevector) != expected_size:
        raise ValueError("Unexpected statevector size.")

    if not np.all(np.isfinite(statevector)):
        raise ValueError("Statevector contains invalid values.")

    return statevector


def calculate_expected_cut(graph, statevector):
    """Calculate the probability-weighted expected Max-Cut value."""

    probabilities = np.abs(statevector) ** 2

    if not np.isclose(probabilities.sum(), 1.0, atol=1e-5):
        raise ValueError("Statevector probabilities do not sum to 1.")

    expected_cut = 0.0

    for index, probability in enumerate(probabilities):
        bitstring = format(index, f"0{graph.n}b")
        expected_cut += probability * cut_value(graph, bitstring)

    return float(expected_cut)


def optimize_qaoa(graph, p, seed=42, maxiter=100):
    """
    Optimize p QAOA layers using COBYLA.

    Parameter order:
        [gamma_1, ..., gamma_p, beta_1, ..., beta_p]
    """

    if p not in (1, 2, 3):
        raise ValueError("This implementation supports p = 1, 2, or 3.")

    if maxiter <= 0:
        raise ValueError("maxiter must be positive.")

    # Preserve the original implementation's initial values.
    initial_gammas = np.full(p, 0.5)
    initial_betas = np.full(p, 0.25)

    initial_parameters = np.concatenate(
        [initial_gammas, initial_betas]
    )

    def objective(parameters):
        gammas = parameters[:p]
        betas = parameters[p:]

        statevector = run_qaoa(graph, gammas, betas)

        expected_cut = calculate_expected_cut(
            graph, statevector
        )

        # SciPy minimizes the objective.
        return -expected_cut

    # Bound every gamma and beta parameter.
    constraints = []

    for index in range(p):
        constraints.append({
            "type": "ineq",
            "fun": lambda x, i=index: x[i]
        })
        constraints.append({
            "type": "ineq",
            "fun": lambda x, i=index: np.pi - x[i]
        })

    for index in range(p, 2 * p):
        constraints.append({
            "type": "ineq",
            "fun": lambda x, i=index: x[i]
        })
        constraints.append({
            "type": "ineq",
            "fun": lambda x, i=index: np.pi / 2 - x[i]
        })

    result = minimize(
        objective,
        x0=initial_parameters,
        method="COBYLA",
        constraints=constraints,
        options={
            "maxiter": maxiter,
            "rhobeg": 0.2,
            "tol": 1e-3,
            "disp": False
        }
    )

    optimized_parameters = np.asarray(result.x)

    optimized_gammas = optimized_parameters[:p]
    optimized_betas = optimized_parameters[p:]

    # Evaluate the final optimized parameters.
    statevector = run_qaoa(
        graph,
        optimized_gammas,
        optimized_betas
    )

    probabilities = np.abs(statevector) ** 2

    expected_cut = calculate_expected_cut(
        graph, statevector
    )

    most_probable_index = int(np.argmax(probabilities))
    most_probable_bitstring = format(
        most_probable_index,
        f"0{graph.n}b"
    )

    most_probable_cut = cut_value(
        graph, most_probable_bitstring
    )

    return {
        "p": p,
        "gammas": optimized_gammas.tolist(),
        "betas": optimized_betas.tolist(),
        "expected_cut": expected_cut,
        "most_probable_bitstring": most_probable_bitstring,
        "most_probable_cut": float(most_probable_cut),
        "probability_sum": float(probabilities.sum()),
        "statevector_size": len(statevector),
        "optimizer_success": bool(result.success),
        "optimizer_message": str(result.message),
        "function_evaluations": int(result.nfev),
        "optimizer_result": result
    }
