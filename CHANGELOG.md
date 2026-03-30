# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-03-29

### Added
- Professional CI/CD pipeline (lint, test, docs, release jobs)
- pytest-cov with 70% coverage gate (achieved 94.85%)
- 29 new unit and E2E tests (51 total)
- Google-style docstrings on all public APIs
- CHANGELOG, CONTRIBUTING, PR template
- GitHub Pages docs via pdoc
- Tag-triggered GitHub Releases
- ruff linting and formatting enforcement

## [1.0.0] - 2026-03-29

### Added

- 15-room castle world with atmospheric descriptions
- Natural language command parsing via Azure AI Foundry LLM
- AI-generated room descriptions tailored to player profile
- 3 victory paths: aggressor, strategist, and explorer
- Adaptive difficulty system that reacts to player behavior
- Player behavior profiling (exploration, aggression, strategy)
- Dynamic world modification (blocked corridors, hidden passages)
- Full CI pipeline with lint, test, docs, and release jobs
- Unit tests for all modules (movement, inventory, combat, AI)
- End-to-end game loop tests for all 3 victory paths
- Google-style docstrings on all public functions
- GitHub Pages documentation via pdoc

[1.0.0]: https://github.com/pjmorr-radpartners/thegiantsdrink/releases/tag/v1.0.0
