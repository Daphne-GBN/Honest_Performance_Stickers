from qiskit_aer import AerSimulator
from qiskit import transpile


def run_circuit(circuit, shots=1000):
    simulator = AerSimulator()
    compiled = transpile(circuit, simulator)

    result = simulator.run(
        compiled,
        shots=shots,
        seed_simulator=42
    ).result()

    return result.get_counts()