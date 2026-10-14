from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

circuit = QuantumCircuit(2, 2)

circuit.h(0)
circuit.cx(0, 1)

circuit.measure([0, 1], [0, 1])

simulator = AerSimulator()

compiled = transpile(circuit, simulator)

result = simulator.run(
    compiled,
    shots=1000,
    seed_simulator=42
).result()

print("Bell-state counts:", result.get_counts())