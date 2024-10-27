# Use an official Python image with a specified version
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Install Qiskit
RUN pip install qiskit

# Copy your project files into the container (adjust paths as needed)
COPY . .

# Run a default command (optional) — e.g., Python interactive shell
CMD ["python"]
