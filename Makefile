# format the code files.
format:
	uvx ruff format && uvx ruff check --fix

test:
	uv python pin 3.13 && uv run pytest

# test different python versions.
test_py312:
	uv python pin 3.12 && uv run pytest

test_py311:
	uv python pin 3.11 && uv run pytest

test_py310:
	uv python pin 3.10 && uv run pytest

test_py39:
	uv python pin 3.9 && uv run pytest

test_py38:
	uv python pin 3.8 && uv run pytest

test-cov:
	uv run pytest --cov=speedtest && uv run coverage html

clean:
	rm -rf build && rm -rf .ruff_cache && rm -rf __pycache__ && rm -rf speedtest.egg-info && rm -rf .pytest_cache && rm -f .coverage && rm -rf htmlcov
