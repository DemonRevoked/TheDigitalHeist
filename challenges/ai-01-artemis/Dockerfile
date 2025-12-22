FROM ubuntu:22.04

# Avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install required tools
RUN apt-get update && apt-get install -y \
    exiftool \
    steghide \
    imagemagick \
    python3 \
    python3-pip \
    wget \
    curl \
    unzip \
    file \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies for image processing
RUN pip3 install --no-cache-dir \
    pillow \
    numpy \
    opencv-python-headless

# Create challenge directory
WORKDIR /challenge

# Copy setup script (for running setup inside container)
COPY setup_challenge.py /challenge/setup_challenge.py

# Copy landing page
COPY index.html /challenge/index.html

# Note: incident_package/ directory and incident_package.zip will be mounted as volumes
# They will be created by setup_challenge.py or mounted from host

# Set permissions
RUN chmod -R 755 /challenge && chmod +x /challenge/setup_challenge.py

# Note: faces/ directory will be mounted as volume

# Expose port for web service
EXPOSE 8000

# Default command - serve files via simple HTTP server
# Serve from /challenge root so index.html is the landing page
# Challenge files are in /challenge/phantom_faces/
CMD ["python3", "-m", "http.server", "8000", "--directory", "/challenge"]

