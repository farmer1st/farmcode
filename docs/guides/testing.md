# Testing Guide

Write and run tests for Farmer Code components.

## Test Categories

| Type | Location | Purpose |
|------|----------|---------|
| Unit | `tests/unit/` | Isolated component tests |
| Integration | `tests/integration/` | Component interaction tests |
| Contract | `tests/contract/` | API contract validation |
| E2E | `tests/e2e/` | Full system tests |

## Running Tests

### All Tests

```bash
uv run pytest
```

### Specific Category

```bash
# Unit tests only
uv run pytest tests/unit/

# Integration tests
uv run pytest tests/integration/

# E2E tests (requires services running)
RUN_E2E_TESTS=1 uv run pytest tests/e2e/
```

### Service-Specific Tests

```bash
# Agent Hub tests
cd services/agent-hub
uv run pytest

# Orchestrator tests
cd services/orchestrator
uv run pytest
```

## Writing Tests

### Unit Test Example

```python
import pytest
from your_module import YourClass

class TestYourClass:
    def test_basic_operation(self):
        obj = YourClass()
        result = obj.do_something("input")
        assert result == "expected"

    def test_error_handling(self):
        obj = YourClass()
        with pytest.raises(ValueError):
            obj.do_something(None)
```

### Contract Test Example

```python
import pytest
from httpx import AsyncClient

@pytest.mark.contract
class TestHealthEndpoint:
    async def test_health_returns_200(self, client: AsyncClient):
        response = await client.get("/health")
        assert response.status_code == 200

    async def test_health_response_format(self, client: AsyncClient):
        response = await client.get("/health")
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
```

### Integration Test Example

```python
import pytest
from unittest.mock import AsyncMock

@pytest.mark.integration
class TestAgentIntegration:
    async def test_agent_invocation(self, mock_claude):
        mock_claude.return_value = "Test response"

        result = await invoke_agent("specify", {"description": "test"})

        assert result["success"] is True
        assert "result" in result
```

## Test Markers

Use pytest markers to categorize tests:

```python
@pytest.mark.unit
def test_unit_example():
    pass

@pytest.mark.integration
def test_integration_example():
    pass

@pytest.mark.contract
def test_contract_example():
    pass

@pytest.mark.e2e
def test_e2e_example():
    pass

@pytest.mark.journey("SVC-001")
def test_user_journey():
    pass
```

## Fixtures

Common fixtures in `conftest.py`:

```python
import pytest
from httpx import AsyncClient

@pytest.fixture
async def client():
    async with AsyncClient(base_url="http://localhost:8000") as c:
        yield c

@pytest.fixture
def mock_claude(mocker):
    return mocker.patch("anthropic.Anthropic")
```

## Coverage

```bash
# Run with coverage
uv run pytest --cov=src/ --cov-report=html

# View report
open htmlcov/index.html
```

## CI Integration

Tests run automatically on PR via GitHub Actions. See `.github/workflows/ci.yml`.
