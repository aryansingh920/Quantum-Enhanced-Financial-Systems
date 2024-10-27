# # from qiskit import QuantumCircuit, Aer, execute
# from qiskit import QuantumCircuit, execute
# from qiskit_aer import Aer

# # Create a simple quantum circuit
# qc = QuantumCircuit(2, 2)
# qc.h(0)
# qc.cx(0, 1)
# qc.measure([0, 1], [0, 1])

# # Run the circuit on the qasm simulator
# simulator = Aer.get_backend('qasm_simulator')
# result = execute(qc, simulator).result()
# counts = result.get_counts()

# print("Result of the circuit:", counts)
from qiskit import QuantumCircuit, execute, BasicAer

# Create a simple quantum circuit
qc = QuantumCircuit(1, 1)
qc.h(0)
qc.measure(0, 0)

# Run the circuit on the BasicAer simulator
simulator = BasicAer.get_backend('qasm_simulator')
result = execute(qc, simulator).result()
print("Test Result:", result.get_counts())
