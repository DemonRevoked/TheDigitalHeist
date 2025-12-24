FROM ubuntu:22.04

# Avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install required tools
RUN echo "=== Installing system packages ===" && \
    apt-get update && apt-get install -y \
    exiftool \
    steghide \
    imagemagick \
    python3 \
    python3-pip \
    wget \
    curl \
    unzip \
    file \
    && rm -rf /var/lib/apt/lists/* && \
    echo "=== System packages installed ===" && \
    exiftool -ver && \
    openssl version && \
    python3 --version

# Install Python dependencies for image processing
RUN echo "=== Installing Python packages ===" && \
    pip3 install --no-cache-dir \
    pillow \
    numpy \
    opencv-python-headless && \
    echo "=== Python packages installed ===" && \
    python3 -c "from PIL import Image; print('✓ PIL/Pillow available')"

# Create challenge directory
WORKDIR /challenge

# Copy setup script
COPY setup_challenge.py /challenge/setup_challenge.py

# Copy landing page
COPY index.html /challenge/index.html

# Copy faces directory (source images)
COPY faces /challenge/faces

# Set permissions
RUN chmod -R 755 /challenge && \
    chmod +x /challenge/setup_challenge.py

# Create startup script that runs setup then starts server
RUN echo '#!/bin/bash' > /challenge/startup.sh && \
    echo 'set -e' >> /challenge/startup.sh && \
    echo 'echo "=== Artemis Challenge Startup ==="' >> /challenge/startup.sh && \
    echo 'cd /challenge' >> /challenge/startup.sh && \
    echo '' >> /challenge/startup.sh && \
    echo '# Run setup to generate challenge files with dynamic key' >> /challenge/startup.sh && \
    echo 'echo "=== Running challenge setup ==="' >> /challenge/startup.sh && \
    echo 'python3 /challenge/setup_challenge.py' >> /challenge/startup.sh && \
    echo '' >> /challenge/startup.sh && \
    echo '# Verify setup' >> /challenge/startup.sh && \
    echo 'if [ -f /challenge/incident_package.zip ]; then' >> /challenge/startup.sh && \
    echo '    echo "✓ incident_package.zip created"' >> /challenge/startup.sh && \
    echo '    ls -lh /challenge/incident_package.zip' >> /challenge/startup.sh && \
    echo 'else' >> /challenge/startup.sh && \
    echo '    echo "✗ incident_package.zip not found!"' >> /challenge/startup.sh && \
    echo '    exit 1' >> /challenge/startup.sh && \
    echo 'fi' >> /challenge/startup.sh && \
    echo '' >> /challenge/startup.sh && \
    echo '# Start web server' >> /challenge/startup.sh && \
    echo 'echo "=== Starting web server on port 8000 ==="' >> /challenge/startup.sh && \
    echo 'exec python3 -m http.server 8000 --directory /challenge' >> /challenge/startup.sh && \
    chmod +x /challenge/startup.sh

# Expose port for web service
EXPOSE 8000

# Run startup script at container start
CMD ["/bin/bash", "/challenge/startup.sh"]

