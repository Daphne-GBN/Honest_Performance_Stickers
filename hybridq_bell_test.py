from hybridq.gate import Gate
from hybridq.circuit import Circuit
from hybridq.circuit.simulation import simulate

# Create Bell-state circuit
circuit = Circuit([
    Gate('H', qubits=[0]),
    Gate('CX', qubits=[0, 1])
])

# Simulate
result = simulate(
    circuit,
    initial_state='00',
    optimize='evolution-einsum'
)

print("Bell State Simulation:")
print(result.reshape(-1))