.PHONY: help install install-dev test lint format type-check clean run build

# Python executable (uses whatever is in PATH - activate your environment first!)
PYTHON := python

# Default target
help:
	@echo "Available commands:"
	@echo "  make install        - Install package in production mode"
	@echo "  make install-dev    - Install package with dev dependencies"
	@echo "  make test           - Run tests"
	@echo "  make lint           - Run ruff linter"
	@echo "  make format         - Format code with black and ruff"
	@echo "  make type-check     - Run mypy type checker"
	@echo "  make clean          - Remove build artifacts and cache"
	@echo "  make run            - Run the CLI (use: make run ARGS='departures Nørreport')"
	@echo "  make build          - Build package distribution"
	@echo ""
	@echo "NOTE: This project uses uv for fast package management."
	@echo "      Install uv: pip install uv"
	@echo "      Activate your Python environment before running these commands!"
	@echo "      (e.g., 'conda activate environment-name' or 'source venv/bin/activate')"

# Install package
install:
	uv pip install -e .

# Install with dev dependencies
install-dev:
	uv pip install -e ".[dev]"

# Run tests
test:
	PYTHONPATH=src $(PYTHON) -m pytest -v

# Run linter
lint:
	$(PYTHON) -m ruff check src/ tests/

# Format code
format:
	$(PYTHON) -m black src/ tests/
	$(PYTHON) -m ruff check --fix src/ tests/

# Type checking
type-check:
	$(PYTHON) -m mypy src/

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Run CLI (example: make run ARGS="departures Nørreport")
run:
	$(PYTHON) -m rejseplanen.cli $(ARGS)

# Build distribution
build:
	uv build

# Combined quality check
check: lint type-check test
	@echo "All checks passed!"

# Setup development environment
setup:
	@echo "Setting up development environment..."
	@echo "1. Install uv (if not already installed):"
	@echo "   pip install uv"
	@echo "2. Create and activate a Python 3.12+ environment:"
	@echo "   - Using conda: conda create -n myenv python=3.12 && conda activate myenv"
	@echo "   - Using venv: python -m venv .venv && source .venv/bin/activate"
	@echo "3. Then run: make install-dev"