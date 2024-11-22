from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

# Create a quantum circuit
qc = QuantumCircuit(2, 2)  # 2 qubits and 2 classical bits
qc.h(0)        # Hadamard gate on qubit 0
qc.cx(0, 1)    # CNOT gate with control qubit 0 and target qubit 1
qc.measure_all()  # Measure all qubits

# Create a simulator
simulator = AerSimulator()

# Run the circuit
job = simulator.run(qc, shots=1000)
result = job.result()

# Get the counts of measurement outcomes
counts = result.get_counts(qc)
print("Measurement counts:", counts)
