# Contributing to The Giant's Drink

Thanks for your interest in contributing! This guide covers the conventions
and workflows used in this project.

## Branch Naming

Use the following prefixes:

| Prefix       | Purpose                        |
|--------------|--------------------------------|
| `feature/`   | New features                   |
| `fix/`       | Bug fixes                      |
| `docs/`      | Documentation only             |
| `chore/`     | Maintenance, CI, dependencies  |
| `test/`      | Adding or updating tests       |

Example: `feature/add-magic-system`

## Commit Messages

This project follows [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>: <short description>

<optional body>
```

Types: `feat`, `fix`, `docs`, `test`, `ci`, `chore`, `refactor`, `style`

## Local Development Setup

```bash
# Clone and enter the repo
git clone https://github.com/pjmorr-radpartners/thegiantsdrink.git
cd thegiantsdrink

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install runtime + dev dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Running Tests

```bash
# Run all tests with verbose output
pytest tests/test_game.py -v

# Run with coverage
pytest tests/test_game.py --cov=. --cov-report=term-missing
```

## Linting

```bash
# Check for lint issues
ruff check .

# Auto-fix what can be fixed
ruff check . --fix

# Format code
ruff format .
```

## Generating Documentation

```bash
# Generate HTML docs with pdoc
pdoc --html --output-dir docs \
  simulation_engine command_parser content_generator \
  behavior_analyzer adaptation_ai game_world main

# Preview locally
python -m http.server --directory docs 8080
```

## Pull Requests

1. Create a feature branch from `main`.
2. Make your changes with conventional commit messages.
3. Ensure all tests pass and `ruff check .` is clean.
4. Open a PR using the repository's pull request template.
5. Request review from a maintainer.
