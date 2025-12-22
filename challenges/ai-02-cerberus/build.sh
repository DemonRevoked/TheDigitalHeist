#!/bin/bash
# Build script for Cerberus CTF Challenge

set -e

echo "Building Cerberus CTF Challenge..."

# Check if running with sudo or as root
if [ "$EUID" -eq 0 ] || sudo -n true 2>/dev/null; then
    DOCKER_CMD="sudo docker-compose"
    DOCKER_CMD_V2="sudo docker compose"
else
    DOCKER_CMD="docker-compose"
    DOCKER_CMD_V2="docker compose"
fi

# Try docker-compose first, fallback to docker compose
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="$DOCKER_CMD"
elif docker compose version &> /dev/null; then
    COMPOSE_CMD="$DOCKER_CMD_V2"
else
    echo "Error: docker-compose not found"
    exit 1
fi

# Clean up any existing containers/images
echo "Cleaning up..."
$COMPOSE_CMD down -v 2>/dev/null || true

# Build and start
echo "Building and starting containers..."
$COMPOSE_CMD up --build -d

echo ""
echo "✓ Build complete!"
echo "API should be available at http://localhost:5000"
echo ""
echo "Test with: curl http://localhost:5000/health"
echo "View logs with: $COMPOSE_CMD logs -f"

