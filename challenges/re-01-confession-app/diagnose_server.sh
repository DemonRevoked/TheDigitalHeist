#!/bin/bash
# Diagnostic script to check server status inside the container

echo "=== Server Diagnostic Script ==="
echo ""

echo "1. Checking if Python3 is available:"
which python3 || echo "ERROR: python3 not found"
python3 --version
echo ""

echo "2. Checking server files:"
ls -la /app/src/server.py /app/src/start_server.sh 2>&1
echo ""

echo "3. Checking CHALLENGE_KEY:"
if [ -n "${CHALLENGE_KEY:-}" ]; then
    echo "CHALLENGE_KEY is set (length: ${#CHALLENGE_KEY})"
else
    echo "ERROR: CHALLENGE_KEY is not set"
    if [ -f "${CHALLENGE_KEY_FILE:-}" ]; then
        echo "Trying to read from CHALLENGE_KEY_FILE: ${CHALLENGE_KEY_FILE}"
        export CHALLENGE_KEY="$(cat "$CHALLENGE_KEY_FILE" 2>/dev/null || echo '')"
        if [ -n "$CHALLENGE_KEY" ]; then
            echo "Successfully read CHALLENGE_KEY from file"
        else
            echo "ERROR: Failed to read CHALLENGE_KEY from file"
        fi
    fi
fi
echo ""

echo "4. Checking if port 31337 is in use:"
if command -v ss >/dev/null 2>&1; then
    ss -tlnp 2>/dev/null | grep ":31337" || echo "Port 31337 is not listening"
elif command -v netstat >/dev/null 2>&1; then
    netstat -tlnp 2>/dev/null | grep ":31337" || echo "Port 31337 is not listening"
else
    echo "Neither ss nor netstat available"
fi
echo ""

echo "5. Checking for Python processes:"
ps aux | grep python | grep -v grep || echo "No Python processes running"
echo ""

echo "6. Checking server log:"
if [ -f /tmp/server.log ]; then
    echo "Server log exists. Last 30 lines:"
    tail -30 /tmp/server.log
else
    echo "ERROR: Server log file /tmp/server.log does not exist"
fi
echo ""

echo "7. Testing server.py syntax:"
cd /app/src
python3 -m py_compile server.py 2>&1 && echo "Syntax OK" || echo "Syntax ERROR"
echo ""

echo "8. Attempting to start server manually (will run for 5 seconds):"
cd /app/src
timeout 5 env CHALLENGE_KEY="${CHALLENGE_KEY:-test-key}" python3 server.py 2>&1 || echo "Server exited or timed out"
echo ""

echo "9. Checking file permissions:"
ls -la /app/src/server.py
ls -la /tmp/server.log 2>/dev/null || echo "/tmp/server.log does not exist"
echo ""

echo "=== Diagnostic Complete ==="

