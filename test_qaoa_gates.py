from hybridq.gate import Gate
from hybridq.circuit import Circuit
from hybridq.circuit.simulation import simulate

import numpy as np

gates = [
    Gate("H", qubits=[0]),
    Gate("CX", qubits=[0, 1]),
    Gate("RZ", qubits=[0], params=[0.5]),
    Gate("RX", qubits=[0], params=[0.5])
]

for gate in gates:
    print("Supported gate:", gate)

circuit = Circuit([
    Gate("H", qubits=[0]),
    Gate("CX", qubits=[0, 1]),
    Gate("RZ", qubits=[0], params=[0.5]),
    Gate("RX", qubits=[1], params=[0.5])
])

result = simulate(
    circuit,
    initial_state="00",
    optimize="evolution-einsum"
)

print("\nCircuit simulation successful!")
print("Statevector:", np.asarray(result).reshape(-1))
