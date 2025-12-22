FROM debian:bookworm-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential openssh-server && \
    rm -rf /var/lib/apt/lists/*

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
    /app/src/evidence_tool.c -o /app/evidence_tool && \
    strip --strip-all /app/evidence_tool

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]
