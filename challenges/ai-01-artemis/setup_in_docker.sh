#!/bin/bash
# Run the setup script inside Docker container where all tools are available

echo "Building Docker image..."
docker-compose build

echo ""
echo "Running setup inside Docker container..."
docker-compose run --rm \
    -v "$(pwd)/phantom_faces:/challenge/phantom_faces" \
    -v "$(pwd)/setup_challenge.py:/challenge/setup_challenge.py:ro" \
    phantom-faces python3 /challenge/setup_challenge.py

echo ""
echo "Setup complete! Files are in phantom_faces/"

