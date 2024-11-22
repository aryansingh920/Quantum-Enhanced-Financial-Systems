from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
import numpy as np
from typing import List, Union


class QuantumRandomGenerator:
    def __init__(self, bits: int = 8):
        """
        Initialize the quantum random number generator
        
        Parameters:
        bits (int): Number of qubits to use (determines range of random numbers)
        """
        self.bits = bits
        self.simulator = AerSimulator()

    def generate_single(self) -> int:
        """Generate a single random number"""
        return self.generate_multiple(shots=1)[0]

    def generate_multiple(self, shots: int) -> List[int]:
        """Generate multiple random numbers"""
        # Create quantum circuit
        qc = QuantumCircuit(self.bits, self.bits)

        # Apply Hadamard gates to create superposition
        for i in range(self.bits):
            qc.h(i)

        # Measure all qubits
        qc.measure_all()

        # Run the circuit
        job = self.simulator.run(qc, shots=shots)
        result = job.result()

        # Process results
        measurements = result.get_counts()
        random_numbers = []
        for bitstring, count in measurements.items():
            # Clean the bitstring by removing spaces
            clean_bitstring = bitstring.replace(' ', '')
            for _ in range(count):
                random_numbers.append(int(clean_bitstring, 2))

        return random_numbers

    def generate_range(self, start: int, end: int, shots: int = 1) -> List[int]:
        """
        Generate random numbers within a specific range
        
        Parameters:
        start (int): Minimum value (inclusive)
        end (int): Maximum value (inclusive)
        shots (int): Number of random numbers to generate
        """
        if start >= end:
            raise ValueError("Start must be less than end")

        range_size = end - start + 1
        required_bits = int(np.ceil(np.log2(range_size)))

        if required_bits > self.bits:
            raise ValueError(
                f"Range too large for current bit size. Max range: 0-{2**self.bits - 1}")

        raw_numbers = self.generate_multiple(shots=shots)

        # Map numbers to desired range
        return [start + (num % range_size) for num in raw_numbers]

    def get_random_float(self, shots: int = 1) -> Union[float, List[float]]:
        """
        Generate random float(s) between 0 and 1
        
        Parameters:
        shots (int): Number of random numbers to generate
        """
        numbers = self.generate_multiple(shots=shots)
        floats = [num / (2**self.bits - 1) for num in numbers]
        return floats[0] if shots == 1 else floats


def plot_distribution(numbers, bits):
    """Plot the distribution of random numbers"""
    import matplotlib.pyplot as plt

    plt.figure(figsize=(12, 6))
    plt.hist(numbers, bins=range(2**bits + 1), density=True, alpha=0.7)
    plt.title('Distribution of Quantum Random Numbers')
    plt.xlabel('Number')
    plt.ylabel('Probability')
    plt.grid(True, alpha=0.3)
    plt.show()


# Example usage
if __name__ == "__main__":
    # Create a quantum random number generator
    qrng = QuantumRandomGenerator(bits=8)

    # print("\n=== Single Random Number ===")
    # print("Random number:", qrng.generate_single())

    # print("\n=== Multiple Random Numbers ===")
    # multiple_numbers = qrng.generate_multiple(shots=5)
    # print("5 random numbers:", multiple_numbers)

    print("\n=== Random Numbers in Range ===")
    range_numbers = qrng.generate_range(0, 10, shots=1)
    print("5 random numbers between 0 and 10:", range_numbers)

    # print("\n=== Random Floats ===")
    # float_numbers = qrng.get_random_float(shots=5)
    # print("5 random floats between 0 and 1:",
    #       [f"{x:.3f}" for x in float_numbers])

    # print("\n=== Distribution Analysis ===")
    # # Generate larger sample for distribution analysis
    # large_sample = qrng.generate_multiple(shots=1000)
    # print(f"Mean of 1000 samples: {np.mean(large_sample):.2f}")
    # print(f"Standard deviation: {np.std(large_sample):.2f}")

    # Plot the distribution
    # plot_distribution(large_sample, qrng.bits)
