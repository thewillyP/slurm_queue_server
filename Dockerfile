# Use the base image with Python 3.13 and bookworm-slim
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim@sha256:f106758c361464e22aa1946c1338ae94de22ec784943494f26485d345dac2d85

# Set environment variable for bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    bash \
    build-essential \
    ca-certificates \
    curl \
    git \
    nano \
    python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set bash as the default shell
SHELL ["/bin/bash", "-c"]

# Set the working directory inside the container
WORKDIR /workspace

# Copy the Python files into the container
COPY queue_server.py .

# Copy the requirements.txt to the container
COPY requirements.txt .

# Install Python dependencies
RUN uv pip install --system --no-cache -r requirements.txt

# Expose the port the app will run on
EXPOSE 5000

# Command to run the queue_server.py script when the container starts
CMD ["python", "queue_server.py"]
