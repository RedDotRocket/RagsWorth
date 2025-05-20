.PHONY: up down build clean logs ps test test-cov install install-dev venv

# Detect if we're using docker compose or docker-compose
DOCKER_COMPOSE := $(shell if command -v docker-compose >/dev/null 2>&1; then echo "docker-compose"; else echo "docker compose"; fi)

# Create virtual environment
venv: install-uv
	@if [ ! -d ".venv" ]; then \
		echo "Creating virtual environment..."; \
		uv venv; \
	else \
		echo "Virtual environment already exists"; \
	fi

# Install uv if not present
install-uv:
	@if ! command -v uv >/dev/null 2>&1; then \
		echo "Installing uv..."; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
	else \
		echo "uv is already installed"; \
	fi

# Install dependencies
install: venv
	. .venv/bin/activate && uv sync --all-groups

# Install development dependencies
install-dev: venv
	. .venv/bin/activate && uv sync --all-groups && uv pip install pytest pytest-cov pymilvus requests pytest-mock

# Start all services
up:
	$(DOCKER_COMPOSE) up -d

# Stop all services
down:
	$(DOCKER_COMPOSE) down

# Build all services
build:
	$(DOCKER_COMPOSE) build

# Remove all containers and volumes
clean:
	$(DOCKER_COMPOSE) down -v

# View logs
logs:
	$(DOCKER_COMPOSE) logs -f

# List running containers
ps:
	$(DOCKER_COMPOSE) ps

# Check service health
health:
	@echo "Checking service health..."
	@$(DOCKER_COMPOSE) ps
	@echo "\nChecking Milvus health..."
	@curl -s http://localhost:9091/api/v1/health || echo "Milvus health check failed"
	@echo "\nChecking MinIO health..."
	@curl -s http://localhost:9000/minio/health/live || echo "MinIO health check failed"
	@echo "\nChecking etcd health..."
	@$(DOCKER_COMPOSE) exec etcd etcdctl endpoint health || echo "etcd health check failed"

# Run tests
test: venv install install-dev
	. .venv/bin/activate && pytest tests/ -v

# Run tests with coverage
test-cov: venv
	. .venv/bin/activate && pytest tests/ -v --cov=. --cov-report=term-missing 