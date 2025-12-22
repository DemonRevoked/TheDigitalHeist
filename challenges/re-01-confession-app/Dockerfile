FROM debian:bookworm-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential openssh-server python3 && \
    rm -rf /var/lib/apt/lists/*

# Prepare sshd
RUN mkdir -p /var/run/sshd

COPY src/ /app/src/

# Build arg for embedding the challenge key at compile time
ARG CHALLENGE_KEY_BUILD=offline-session-key

# Compile with maximum obfuscation: stripped, no debug info, no symbols
# Makes binary unreadable with basic tools, requires RE tools like Ghidra
RUN gcc -O2 -s -fno-stack-protector -fno-ident \
    -fno-asynchronous-unwind-tables -fno-unwind-tables \
    -ffunction-sections -fdata-sections \
    -Wl,--build-id=none -Wl,--gc-sections \
    -DCHALLENGE_KEY_BUILD=\"${CHALLENGE_KEY_BUILD}\" \
    /app/src/confession_app.c -o /app/confession_app && \
    strip --strip-all /app/confession_app

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Copy and setup server script
COPY src/server.py /app/src/server.py
RUN chmod +x /app/src/server.py

# Copy server startup wrapper
COPY src/start_server.sh /app/src/start_server.sh
RUN chmod +x /app/src/start_server.sh

# Copy diagnostic script
COPY diagnose_server.sh /app/diagnose_server.sh
RUN chmod +x /app/diagnose_server.sh

# Create default basics.txt (will be moved to /root/.flag_storage by entrypoint)
# This file is only accessible by root, not by SSH user
RUN echo "TDHCTF{confession_gateway_phrase}" > /app/basics.txt && \
    chmod 600 /app/basics.txt

CMD ["/app/entrypoint.sh"]
