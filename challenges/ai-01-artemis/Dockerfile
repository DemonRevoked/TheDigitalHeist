FROM ubuntu:22.04

# Avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install required tools
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*
# Install Python dependencies for image processing
RUN pip3 install --no-cache-dir \
    pillow \
    numpy \
    opencv-python-headless
# Create challenge directory
WORKDIR /challenge
# Copy landing page
COPY index.html /challenge/index.html

# Expose port for web service
EXPOSE 8000

CMD ["python3", "-m", "http.server", "8000", "--directory", "/challenge"]

