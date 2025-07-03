FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    tar \
    && rm -rf /var/lib/apt/lists/*

# Install Docker CLI (for Grype)
RUN curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh

# Install Go (for TruffleHog v3)
RUN wget https://go.dev/dl/go1.21.0.linux-amd64.tar.gz && \
    tar -C /usr/local -xzf go1.21.0.linux-amd64.tar.gz && \
    rm go1.21.0.linux-amd64.tar.gz

ENV PATH="/usr/local/go/bin:${PATH}"

# Install Semgrep
RUN pip install semgrep

# Install Grype
RUN curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s -- -b /usr/local/bin

# Install TruffleHog via pip (more stable)
RUN pip install truffleHog

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p output temp bot_output bot_temp

# Expose port for web interface (if needed)
EXPOSE 8000

# Default command
CMD ["python", "run.py"]