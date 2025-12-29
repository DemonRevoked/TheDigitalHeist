#!/bin/bash

# Deployment script for Money Heist CTF Challenge
# This script helps creators deploy the challenge using Docker

set -e

echo "=========================================="
echo "Money Heist CTF - Deployment Script"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Load environment variables from .env if it exists
if [ -f .env ]; then
    echo "📄 Loading environment variables from .env file..."
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "⚠️  No .env file found. Using default values."
    echo "   Create a .env file with PORT, KEY, and FLAG for production."
fi

# Set defaults if not set
export PORT=${PORT:-5101}
export KEY=${KEY:-RDxlT2USNk6yFo1Ejmenl1tkrJ4vGz9T2YKrqOQT}
export FLAG=${FLAG:-TDHCTF{BELLA_CIAO_NO_MORE_DOT_DOT_SLASH}}

echo ""
echo "Configuration:"
echo "  PORT: $PORT"
echo "  KEY: ${KEY:0:20}..." # Show only first 20 chars
echo "  FLAG: ${FLAG:0:30}..." # Show only first 30 chars
echo ""

# Build and start
echo "🔨 Building Docker image..."
if docker compose version &> /dev/null; then
    docker compose build
else
    docker-compose build
fi

echo ""
echo "🚀 Starting containers..."
if docker compose version &> /dev/null; then
    docker compose up -d
else
    docker-compose up -d
fi

# Wait for server to start
echo ""
echo "⏳ Waiting for server to start..."
sleep 5

# Check health
echo "🏥 Checking server health..."
HEALTH=$(curl -s http://localhost:${PORT}/health 2>/dev/null || echo "failed")

if echo "$HEALTH" | grep -q "ok"; then
    echo "✅ Server is healthy!"
    echo ""
    echo "=========================================="
    echo "✅ Deployment Successful!"
    echo "=========================================="
    echo ""
    echo "Challenge is now available at:"
    echo "  http://localhost:${PORT}"
    echo ""
    echo "For remote access, use:"
    echo "  http://<your-server-ip>:${PORT}"
    echo ""
    echo "Health check:"
    echo "  http://localhost:${PORT}/health"
    echo ""
    echo "To view logs:"
    if docker compose version &> /dev/null; then
        echo "  docker compose logs -f web"
    else
        echo "  docker-compose logs -f web"
    fi
    echo ""
    echo "To stop:"
    if docker compose version &> /dev/null; then
        echo "  docker compose down"
    else
        echo "  docker-compose down"
    fi
else
    echo "❌ Server health check failed!"
    echo "   Response: $HEALTH"
    echo ""
    echo "Check logs:"
    if docker compose version &> /dev/null; then
        docker compose logs web
    else
        docker-compose logs web
    fi
    exit 1
fi

