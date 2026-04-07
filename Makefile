.PHONY: help install dev test lint format clean docker-build docker-run docker-logs

help:
	@echo "QuickGlance Development Commands"
	@echo "=================================="
	@echo "make install       - Install dependencies"
	@echo "make dev           - Run development environment"
	@echo "make cli           - Run CLI version"
	@echo "make web           - Run Streamlit web UI"
	@echo "make test          - Run tests"
	@echo "make lint          - Run linting"
	@echo "make format        - Format code with black"
	@echo "make clean         - Clean up cache and logs"
	@echo "make docker-build  - Build Docker image"
	@echo "make docker-run    - Run Docker container"
	@echo "make docker-logs   - Show Docker logs"

install:
	pip install -r requirements.txt

dev:
	@echo "Starting development environment..."
	streamlit run app.py --logger.level=debug

cli:
	python main.py

web:
	streamlit run app.py

test:
	pytest tests_example.py -v --tb=short

lint:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

format:
	black . --line-length 100
	isort . --profile black

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	rm -f logs/app.log*
	rm -rf .eggs *.egg-info dist build

docker-build:
	docker build -t quickglance:latest .

docker-run:
	docker run -p 8501:8501 --env-file .env quickglance:latest

docker-logs:
	docker logs -f quickglance-app

docker-compose-up:
	docker-compose up --build

docker-compose-down:
	docker-compose down

docker-compose-logs:
	docker-compose logs -f

requirements-freeze:
	pip freeze > requirements-frozen.txt

check-env:
	@if [ ! -f .env ]; then \
		echo "Creating .env from .env.example..."; \
		cp .env.example .env; \
		echo "⚠️  Please update .env with your API keys"; \
	else \
		echo "✓ .env file exists"; \
	fi

setup: check-env install
	@echo "✓ Setup complete!"
	@echo "Next steps:"
	@echo "  1. Edit .env with your API keys"
	@echo "  2. Run: make web (for web UI) or make cli (for CLI)"
