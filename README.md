# The Giant's Drink

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue)](https://www.python.org/)
[![CI Pipeline](https://github.com/pjmorr-radpartners/thegiantsdrink/actions/workflows/ci.yml/badge.svg)](https://github.com/pjmorr-radpartners/thegiantsdrink/actions)

A text-based adventure game where you explore a castle, collect items, and face a giant. The game uses AI (via Azure AI Foundry) to parse natural language commands, generate atmospheric room descriptions, and adapt difficulty to your playstyle.

## Features

- **Natural language commands** — type freely; an LLM parses your intent
- **15 rooms** with rich, atmospheric descriptions inspired by Ender's Game's Mind Game
- **3 paths to victory** — aggressor, strategist, or explorer
- **Adaptive difficulty** — the game watches how you play and adjusts the world accordingly
- **Player profiling** — the behavior analyzer tracks your play style and tailors content

## Setup

```bash
# Clone the repository
git clone https://github.com/pjmorr-radpartners/thegiantsdrink.git
cd thegiantsdrink

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt
```

## Required Environment Variables

Set these before running the game:

| Variable | Description |
|---|---|
| `AZURE_API_KEY` | Your Azure AI Foundry API key |
| `AZURE_API_BASE` | Endpoint base URL (e.g. `https://xxx.services.ai.azure.com/...`) |
| `AZURE_API_MODEL` | Model name to use for completions |

```bash
export AZURE_API_KEY="your-api-key"
export AZURE_API_BASE="https://your-endpoint.services.ai.azure.com/openai/v1"
export AZURE_API_MODEL="your-model-name"
```

## How to Run

```bash
python main.py
```

## How to Play

| Command | Description |
|---|---|
| `look` | Look around the current room |
| `go <direction>` | Move north, south, east, west, up, or down |
| `take <item>` | Pick up an item |
| `use <item>` | Use an item from your inventory |
| `attack <target>` | Attack something |
| `inventory` | Check your inventory |
| `help` | Show available commands |
| `quit` / `exit` | Leave the game |

## Running Tests

```bash
pytest tests/test_game.py -v
```

## Local Development

### Prerequisites
- Python 3.9 or higher
- Git

### Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Set environment variables (required for Azure AI Foundry)
export AZURE_API_KEY="your-key"
export AZURE_API_BASE="https://your-endpoint.services.ai.azure.com/openai/v1"
export AZURE_API_MODEL="your-model-name"
```

### Development Commands

```bash
# Format code with Ruff
ruff format .

# Lint and fix issues
ruff check --fix .

# Run all tests
pytest tests/test_game.py -v

# Run with coverage
pytest tests/test_game.py --cov=. --cov-report=html

# Generate API documentation
pdoc --serve simulation_engine behavior_analyzer adaptation_ai content_generator

# Play the game locally
python main.py
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for branch naming, commit conventions, and development workflow.

This project follows [Conventional Commits](https://www.conventionalcommits.org) for all commit messages.

## Documentation

- [API Documentation](https://pjmorr-radpartners.github.io/thegiantsdrink/) — Generated from docstrings
- [Changelog](CHANGELOG.md) — Version history and release notes
- [Contributing Guide](CONTRIBUTING.md) — How to contribute
