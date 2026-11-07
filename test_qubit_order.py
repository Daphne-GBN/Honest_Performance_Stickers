
import numpy as np
from hybridq.gate import Gate
from hybridq.circuit import Circuit
from hybridq.circuit.simulation import simulate

# Activate both qubits using actual operations.
circuit = Circuit([
    Gate("X", qubits=[0]),
    Gate("H", qubits=[1])
])

result = simulate(
    circuit,
    initial_state="00",
    optimize="evolution-einsum",
    simplify=False,
    remove_id_gates=False
)

state = np.asarray(result).reshape(-1)

print("Statevector:", state)
print("Probabilities:", np.abs(state) ** 2)
print("Most likely basis-state indices:",
      np.where(np.abs(state) ** 2 > 1e-6)[0])
