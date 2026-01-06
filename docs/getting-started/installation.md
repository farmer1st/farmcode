# Installation

## Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- Git
- Docker (for running services locally)

## Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with Homebrew
brew install uv
```

## Clone the Repository

```bash
git clone https://github.com/farmer1st/farmer-code.git
cd farmer-code
```

## Install Dependencies

```bash
# Create virtual environment and install
uv sync

# Install dev dependencies
uv pip install -e ".[dev]"
```

## Verify Installation

```bash
# Run tests
uv run pytest

# Check linting
uv run ruff check src/ tests/
```

## Next Steps

- [Quick Start](quickstart.md) - Run your first workflow
- [Development Workflow](development.md) - Set up your dev environment
