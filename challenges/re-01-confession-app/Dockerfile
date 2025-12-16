FROM debian:bookworm-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential openssh-server && \
    rm -rf /var/lib/apt/lists/*

# Prepare sshd
RUN mkdir -p /var/run/sshd

COPY src/ /app/src/
RUN gcc -O2 -s /app/src/confession_app.c -o /app/confession_app

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]
