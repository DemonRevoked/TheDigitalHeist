#!/bin/bash
# Wrapper script to start the server and keep it running

cd /app/src || cd "$(dirname "$0")"

# Ensure log directory exists
mkdir -p /tmp
touch /tmp/server.log

# Start server, redirecting all output
# Don't use exec here - we want the shell to remain so PID tracking works
python3 server.py >> /tmp/server.log 2>&1
