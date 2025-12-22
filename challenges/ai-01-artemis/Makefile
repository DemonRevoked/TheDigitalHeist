.PHONY: setup setup-docker build up down clean verify package help

help:
	@echo "Phantom Faces CTF Challenge - Makefile"
	@echo ""
	@echo "Available commands:"
	@echo "  make setup        - Generate all challenge files (local, may need tools)"
	@echo "  make setup-docker - Generate challenge files in Docker (recommended)"
	@echo "  make build        - Build Docker image"
	@echo "  make up           - Start challenge container"
	@echo "  make down         - Stop challenge container"
	@echo "  make verify       - Verify challenge setup"
	@echo "  make package      - Create zip file for CTFd"
	@echo "  make clean        - Remove generated files and containers"
	@echo "  make help         - Show this help message"

setup:
	@echo "Setting up challenge files (local)..."
	@echo "Note: Requires exiftool and steghide. Use 'make setup-docker' for full setup."
	python3 setup_challenge.py

setup-docker:
	@echo "Setting up challenge files in Docker (recommended)..."
	./setup_in_docker.sh

build: setup
	@echo "Building Docker image..."
	docker-compose build

up:
	@echo "Starting challenge container..."
	docker-compose up -d
	@echo "Challenge available at http://localhost:8000"

down:
	@echo "Stopping challenge container..."
	docker-compose down

verify:
	@echo "Verifying challenge setup..."
	python3 verify_challenge.py

package: setup
	@echo "Packaging challenge for CTFd..."
	./package_challenge.sh

clean:
	@echo "Cleaning up..."
	docker-compose down -v 2>/dev/null || true
	rm -f phantom_faces.zip
	rm -f hidden_msg.txt
	rm -f CTFD_DESCRIPTION.md
	@echo "Clean complete"

