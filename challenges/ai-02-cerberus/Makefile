.PHONY: build up down restart logs test verify clean

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

restart: down up

logs:
	docker-compose logs -f

test:
	python verify_solution.py

verify: up
	sleep 5
	python verify_solution.py

clean:
	docker-compose down -v
	rm -rf models/ __pycache__/ *.pyc

help:
	@echo "Available commands:"
	@echo "  make build    - Build Docker images"
	@echo "  make up       - Start containers"
	@echo "  make down     - Stop containers"
	@echo "  make restart  - Restart containers"
	@echo "  make logs     - View container logs"
	@echo "  make verify   - Start and verify challenge"
	@echo "  make clean    - Clean up containers and files"

