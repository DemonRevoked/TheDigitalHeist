FROM sagemath/sagemath:latest

USER root

WORKDIR /app

# Install additional packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Install pycryptodome for the Crypto module in Sage's Python environment
# SageMath uses its own Python, so we need to use sage -pip
RUN sage -pip install --no-cache-dir pycryptodome

# Copy encryption script
COPY src/ /app/src/
RUN chmod +x /app/src/1337crypt.sage

# Copy entrypoint
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]

