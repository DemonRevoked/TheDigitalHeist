#!/bin/bash
#
# Wrapper script to run CTF validation inside the Docker container
# Usage: ./run_validation.sh
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTAINER_NAME="exp-01-berlinslocker_lockerctl-medium_1"

echo "Checking if container is running..."
if ! sudo docker ps | grep -q "$CONTAINER_NAME"; then
    echo "ERROR: Container $CONTAINER_NAME is not running!"
    echo "Please start it with: docker-compose up -d"
    exit 1
fi

echo "Copying validation script to container..."
sudo docker cp "$SCRIPT_DIR/validate_ctf.sh" "$CONTAINER_NAME:/tmp/validate_ctf.sh"

echo "Running validation script..."
echo ""
sudo docker exec "$CONTAINER_NAME" bash -c "chmod +x /tmp/validate_ctf.sh && su tokyo -c '/tmp/validate_ctf.sh'"

