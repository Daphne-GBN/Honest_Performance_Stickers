from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error


def build_qaoa_circuit():
    circuit = QuantumCircuit(2, 2)

    circuit.h(0)
    circuit.h(1)
    circuit.cx(0, 1)

    circuit.rz(0.5, 0)
    circuit.rz(0.5, 1)

    circuit.cx(0, 1)

    circuit.measure([0, 1], [0, 1])

    return circuit


def run_noiseless(circuit):
    simulator = AerSimulator()
    compiled = transpile(circuit, simulator)

    result = simulator.run(
        compiled,
        shots=1000,
        seed_simulator=42
    ).result()

    return result.get_counts()


def run_with_noise(circuit):
    noise = NoiseModel()

    error1 = depolarizing_error(0.01, 1)
    error2 = depolarizing_error(0.02, 2)

    noise.add_all_qubit_quantum_error(error1, ["h", "rz"])
    noise.add_all_qubit_quantum_error(error2, ["cx"])

    simulator = AerSimulator(noise_model=noise)
    compiled = transpile(circuit, simulator)

    result = simulator.run(
        compiled,
        shots=1000,
        seed_simulator=42
    ).result()

    return result.get_counts()


if __name__ == "__main__":
    circuit = build_qaoa_circuit()

    print("QAOA circuit:")
    print(circuit)

    noiseless_counts = run_noiseless(circuit)
    print("\nNoiseless QAOA counts:", noiseless_counts)

    noisy_counts = run_with_noise(circuit)
    print("Depolarizing-noise QAOA counts:", noisy_counts)

    print("\nAer validation: PASS")