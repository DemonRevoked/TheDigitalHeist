#!/usr/bin/env bash
set -euo pipefail

# Configure student SSH user (storyline-friendly)
STUDENT_USER="${STUDENT_USER:-rio}"
STUDENT_PASS="${STUDENT_PASS:-RedCipher@1}"

if ! id "$STUDENT_USER" >/dev/null 2>&1; then
  useradd -m -s /bin/bash "$STUDENT_USER"
fi
echo "$STUDENT_USER:$STUDENT_PASS" | chpasswd

# Start sshd
/usr/sbin/sshd

# Read key from file or env; no local generation fallback (keys come from host startup.sh).
if [ -n "${CHALLENGE_KEY_FILE:-}" ] && [ -f "$CHALLENGE_KEY_FILE" ]; then
  export CHALLENGE_KEY="$(cat "$CHALLENGE_KEY_FILE")"
elif [ -n "${CHALLENGE_KEY:-}" ]; then
  export CHALLENGE_KEY
else
  echo "CHALLENGE_KEY not provided; set CHALLENGE_KEY or mount CHALLENGE_KEY_FILE." >&2
  exit 1
fi

# Start the passphrase validation server in background with CHALLENGE_KEY
# Run server as root to access secure flag file
# First, check if port is already in use and kill any existing server
if command -v ss >/dev/null 2>&1; then
    EXISTING_PID=$(ss -tlnp 2>/dev/null | grep ":31337" | grep -oP 'pid=\K[0-9]+' | head -1)
    if [ -n "$EXISTING_PID" ]; then
        kill "$EXISTING_PID" 2>/dev/null || true
        sleep 1
    fi
fi

# Start server with proper logging - start Python directly for better PID tracking
# Ensure log directory exists and is writable
mkdir -p /tmp
touch /tmp/server.log
chmod 666 /tmp/server.log 2>/dev/null || true

cd /app/src
# Start server and capture both stdout and stderr
env CHALLENGE_KEY="$CHALLENGE_KEY" python3 server.py >> /tmp/server.log 2>&1 &
SERVER_PID=$!
sleep 3  # Give server time to start

# Verify server started and is listening
SERVER_RUNNING=0
for i in {1..10}; do
    if kill -0 $SERVER_PID 2>/dev/null; then
        if (command -v ss >/dev/null 2>&1 && ss -tlnp 2>/dev/null | grep -q ":31337") || \
           (command -v netstat >/dev/null 2>&1 && netstat -tlnp 2>/dev/null | grep -q ":31337"); then
            SERVER_RUNNING=1
            break
        fi
    else
        # Process died, check log
        echo "Server process died. Checking log..." >&2
        cat /tmp/server.log >&2 || echo "(log file empty)" >&2
        # Try to restart
        env CHALLENGE_KEY="$CHALLENGE_KEY" python3 /app/src/server.py >> /tmp/server.log 2>&1 &
        SERVER_PID=$!
        sleep 2
    fi
    sleep 1
done

if [ $SERVER_RUNNING -eq 0 ]; then
    echo "ERROR: Server failed to start or bind to port 31337" >&2
    echo "Server log:" >&2
    if [ -f /tmp/server.log ]; then
        cat /tmp/server.log >&2
    else
        echo "(log file does not exist)" >&2
    fi
    echo "Attempting to start server directly to see error..." >&2
    # Try one more time with direct start and show output
    cd /app/src
    env CHALLENGE_KEY="$CHALLENGE_KEY" python3 server.py >> /tmp/server.log 2>&1 &
    SERVER_PID=$!
    sleep 3
    # Check if it's running now
    if kill -0 $SERVER_PID 2>/dev/null && (ss -tlnp 2>/dev/null | grep -q ":31337" || netstat -tlnp 2>/dev/null | grep -q ":31337"); then
        echo "Server started successfully on retry" >&2
    else
        echo "Server still not running. Last 20 lines of log:" >&2
        tail -20 /tmp/server.log >&2 || echo "(log file empty)" >&2
    fi
    # Don't exit - let container continue, server might start later
fi

# Prevent user from reading server's environment via /proc
# (Server runs as root, user cannot access /proc/$SERVER_PID/environ anyway)

# Move challenge binary into the student home so the user only interacts there.
APP_DIR="/home/${STUDENT_USER}/confession"
mkdir -p "$APP_DIR"
cp /app/confession_app "$APP_DIR/."
# DO NOT copy flag file to user directory - only server should access it
chown -R "${STUDENT_USER}:${STUDENT_USER}" "$APP_DIR"
chmod 700 "/home/${STUDENT_USER}"

# Store flag in secure location (root-only access)
FLAG_FILE="/root/.flag_storage"
if [ -f "/app/basics.txt" ]; then
  cp /app/basics.txt "$FLAG_FILE"
elif [ -f "/challenge-files/re-01-confession-app/basics.txt" ]; then
  cp /challenge-files/re-01-confession-app/basics.txt "$FLAG_FILE"
else
  echo "TDHCTF{confession_gateway_phrase}" > "$FLAG_FILE"
fi
chmod 600 "$FLAG_FILE"
chown root:root "$FLAG_FILE"

# Copy compiled binary to shared challenge-files mount so the landing
# page can expose it for direct download without SSH access.
if [ -d "/challenge-files/re-01-confession-app" ]; then
  cp /app/confession_app /challenge-files/re-01-confession-app/confession_app
  chmod 755 /challenge-files/re-01-confession-app/confession_app || true
fi

# Lock down build artifacts so the student user cannot read them.
chmod 700 /app

# DO NOT expose CHALLENGE_KEY to user environment - only server should have it
# Remove any existing key files from user directory
rm -f "/home/${STUDENT_USER}/.confession_env"
# Remove any bashrc references to prevent key exposure
sed -i '/source ~\/.confession_env/d' "/home/${STUDENT_USER}/.bashrc" 2>/dev/null || true

# Keep container running (server runs in background, SSH handles connections)
# Wait for server to be ready and verify it's listening
sleep 3
if command -v ss >/dev/null 2>&1 && ss -tlnp 2>/dev/null | grep -q ":31337"; then
    echo "Server started on localhost:31337" >&2
elif command -v netstat >/dev/null 2>&1 && netstat -tlnp 2>/dev/null | grep -q ":31337"; then
    echo "Server started on localhost:31337" >&2
else
    echo "Warning: Server may not be listening on port 31337" >&2
    echo "Check /tmp/server.log for errors" >&2
    # Try to restart server
    cd /app/src
    env CHALLENGE_KEY="$CHALLENGE_KEY" python3 server.py >> /tmp/server.log 2>&1 &
    SERVER_PID=$!
    sleep 2
fi

# Additional security: Ensure user cannot access server process info
# (Server runs as root, user already cannot access /proc/$SERVER_PID/*)
# User can still make HTTP requests to localhost:31337, but needs correct passphrase

# Keep container alive and monitor server
while true; do
    # Check if server process is still running
    if ! kill -0 $SERVER_PID 2>/dev/null; then
        echo "Server process died, restarting..." >&2
        cd /app/src
        env CHALLENGE_KEY="$CHALLENGE_KEY" python3 server.py >> /tmp/server.log 2>&1 &
        SERVER_PID=$!
        sleep 3
        # Verify it started
        if ! kill -0 $SERVER_PID 2>/dev/null; then
            echo "Failed to restart server. Last 20 lines of log:" >&2
            tail -20 /tmp/server.log >&2 || echo "(log file empty)" >&2
        fi
    fi
    sleep 60  # Check every minute instead of every hour
done
