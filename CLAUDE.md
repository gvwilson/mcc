# MCC Project System Prompt

## Instructions for Claude

Follow these guidelines when working on this project:

1. Keep code simple and readable.
2. NEVER add unnecessary whitespace in Python files.
3. Follow Python best practices with meaningful variable names.
4. Add tests for all new functionality.
5. Refactor to remove duplication when possible.
6. NEVER add excessive comments that just repeat information in code.
7. Use Path objects from pathlib rather than string manipulation.
8. ALWAYS run Python commands in the virtual environment (.venv).
9. ALWAYS add new packages to pyproject.toml instead of installing directly.
10. ALWAYS use uv for package management.
11. ALWAYS use ruff for linting and code formatting.

## Common Commands

- Activate virtual environment: `source .venv/bin/activate`
- Run commands in virtual environment: `source .venv/bin/activate && python [command]`
- Add package to project: `uv pip add [package] --to pyproject.toml`
- Install project dependencies: `uv pip install -e ".[dev]"`
- Run tests: `source .venv/bin/activate && python -m pytest`
- Lint code: `source .venv/bin/activate && ruff check mccole tests`
- Format code: `source .venv/bin/activate && ruff format mccole tests`
