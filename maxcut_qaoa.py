
from pathlib import Path
from scipy.optimize import minimize
import numpy as np

from hybridq.gate import Gate
from hybridq.circuit import Circuit
from hybridq.circuit.simulation import simulate


# --------------------------------------------------
# 1. Load a Max-Cut graph
# --------------------------------------------------

def load_graph(file_path):

    with open(file_path, "r") as file:
        lines = [
            line.strip()
            for line in file
            if line.strip()
        ]

    n, m = map(int, lines[0].split())

    edges = []

    for line in lines[1:]:
        u, v, weight = line.split()

        # Convert 1-indexed vertices to 0-indexed qubits
        u = int(u) - 1
        v = int(v) - 1
        weight = float(weight)

        if not (0 <= u < n and 0 <= v < n):
            raise ValueError(f"Invalid edge: {line}")

        edges.append((u, v, weight))

    if len(edges) != m:
        raise ValueError(f"Expected {m} edges, found {len(edges)}")

    return n, edges


# --------------------------------------------------
# 2. Calculate Max-Cut objective
# --------------------------------------------------

def calculate_cut_value(edges, bitstring):

    return sum(
        weight
        for u, v, weight in edges
        if bitstring[u] != bitstring[v]
    )


# --------------------------------------------------
# 3. Construct the QAOA circuit
# --------------------------------------------------

def build_qaoa_circuit(n, edges, gamma, beta):

    gates = []

    # Stage 1: Initial superposition
    for qubit in range(n):
        gates.append(
            Gate("H", qubits=[qubit])
        )

    # Stage 2: Cost unitary
    for u, v, weight in edges:

        gates.append(
            Gate("CX", qubits=[u, v])
        )

        gates.append(
            Gate("RZ", qubits=[v], params=[-gamma * weight])
        )

        gates.append(
            Gate("CX", qubits=[u, v])
        )

    # Stage 3: Mixer unitary
    for qubit in range(n):

        gates.append(
            Gate("RX", qubits=[qubit], params=[2 * beta])
        )

    return Circuit(gates)


# --------------------------------------------------
# 4. Simulate QAOA using HybridQ
# --------------------------------------------------

def run_qaoa(n, edges, gamma, beta):

    circuit = build_qaoa_circuit(
        n, edges, gamma, beta
    )

    result = simulate(
        circuit,
        initial_state="0" * n,
        optimize="evolution-einsum",
        simplify=False
    )

    statevector = np.asarray(result).reshape(-1)

    return statevector


# --------------------------------------------------
# 5. Calculate expected cut value
# --------------------------------------------------

def calculate_expected_cut(n, edges, statevector):

    probabilities = np.abs(statevector) ** 2

    expected_value = 0.0

    for index, probability in enumerate(probabilities):

        # Qubit 0 is the leftmost bit
        bitstring = format(index, f"0{n}b")

        cut_value = calculate_cut_value(
            edges, bitstring
        )

        expected_value += probability * cut_value

    return expected_value

# --------------------------------------------------
# 6. Optimize QAOA parameters using COBYLA
# --------------------------------------------------

def optimize_qaoa(n, edges):

    def objective(parameters):

        gamma, beta = parameters

        statevector = run_qaoa(
            n, edges, gamma, beta
        )

        expected_cut = calculate_expected_cut(
            n, edges, statevector
        )

        # SciPy minimizes, so negate the cut value
        return -expected_cut

    result = minimize(
        objective,
        x0=[0.5, 0.25],
        method="COBYLA",
        constraints=[
            {"type": "ineq", "fun": lambda x: x[0]},
            {"type": "ineq", "fun": lambda x: np.pi - x[0]},
            {"type": "ineq", "fun": lambda x: x[1]},
            {"type": "ineq", "fun": lambda x: np.pi / 2 - x[1]}
        ],
        options={
            "maxiter": 40,
            "rhobeg": 0.2,
            "tol": 1e-3,
            "disp": True
        }
    )

    return result


# --------------------------------------------------
# 7. Run the first QAOA experiment
# --------------------------------------------------

if __name__ == "__main__":

    print("\nHYBRIDQ MAX-CUT QAOA")
    print("-------------------")

    # Load the graph
    graph_path = Path("maxcut_instances/instances/cycle_n10_s0.txt")

    n, edges = load_graph(graph_path)

    print("Graph:", graph_path.name)
    print("Vertices:", n)
    print("Edges:", len(edges))

    # Optimize QAOA parameters
    print("\nPARAMETER OPTIMIZATION")
    print("----------------------")

    optimization_result = optimize_qaoa(n, edges)

    gamma, beta = optimization_result.x

    print("\nOPTIMIZED PARAMETERS")
    print("--------------------")
    print("Gamma:", gamma)
    print("Beta:", beta)
    print("Optimizer success:", optimization_result.success)

    # Simulate using optimized parameters
    statevector = run_qaoa(n, edges, gamma, beta)

    probabilities = np.abs(statevector) ** 2

    expected_cut = calculate_expected_cut(
        n, edges, statevector
    )

    best_index = int(np.argmax(probabilities))
    best_bitstring = format(best_index, f"0{n}b")

    best_cut = calculate_cut_value(edges, best_bitstring)

    print("\nOPTIMIZED QAOA RESULTS")
    print("----------------------")
    print("Statevector size:", len(statevector))
    print("Probability sum:", probabilities.sum())
    print("Most probable bitstring:", best_bitstring)
    print("Cut value of most probable bitstring:", best_cut)
    print("Expected cut value:", expected_cut)
