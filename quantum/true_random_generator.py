from qiskit import QuantumCircuit, Aer, execute
import numpy as np


def quantum_random_number(min_val, max_val):
    # Calculate the number of qubits needed to represent the range
    range_size = max_val - min_val + 1
    # Qubits needed to cover the range
    num_qubits = int(np.ceil(np.log2(range_size)))

    # Create a quantum circuit with the required number of qubits and classical bits
    qc = QuantumCircuit(num_qubits, num_qubits)

    # Apply Hadamard gates to all qubits to create a superposition
    for qubit in range(num_qubits):
        qc.h(qubit)

    # Measure the qubits
    qc.measure(range(num_qubits), range(num_qubits))

    # Use a simulator to execute the circuit
    simulator = Aer.get_backend('qasm_simulator')
    # Single shot for a single random number
    result = execute(qc, simulator, shots=1).result()
    counts = result.get_counts()

    # Get the measured bitstring (binary number)
    random_binary = list(counts.keys())[0]
    random_number = int(random_binary, 2)  # Convert binary string to decimal

    # Map the number to the specified range
    scaled_random_number = min_val + (random_number % range_size)
    return scaled_random_number


# Example usage
min_value = -1
max_value = 1
random_number = quantum_random_number(min_value, max_value)
print(f"Random number between {min_value} and {max_value}: {random_number}")
