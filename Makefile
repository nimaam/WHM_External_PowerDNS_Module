.PHONY: install uninstall test lint format clean

install:
	sudo ./install.sh

uninstall:
	sudo ./uninstall.sh

test:
	pytest tests/ -v --cov=src/ultahost_dns --cov-report=html

lint:
	ruff check src/ tests/
	ruff format --check src/ tests/

format:
	ruff format src/ tests/
	ruff check --fix src/ tests/

clean:
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf dist
	rm -rf build


