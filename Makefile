.PHONY: install test clean

install:
	python3 -m venv .venv
	.venv/bin/pip install -e ".[dev]"

test:
	.venv/bin/python -m pytest

clean:
	rm -rf .venv build dist *.egg-info __pycache__ .pytest_cache
