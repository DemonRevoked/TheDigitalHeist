FROM debian:bookworm-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    openssh-server && \
    rm -rf /var/lib/apt/lists/*

# Install Python crypto libraries
RUN pip3 install --no-cache-dir pycryptodome --break-system-packages

# Prepare sshd
RUN mkdir -p /var/run/sshd

# Copy encryption script
COPY src/ /app/src/
RUN chmod +x /app/src/encrypt.py

# Copy entrypoint
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]

