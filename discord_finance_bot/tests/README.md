# Tests Directory

This directory contains the test suite for the Discord Finance Bot.

## Quick Start

### Run All Tests
```bash
# Using the test runner script
./run_tests.sh

# Or using pytest directly
pytest tests/ -v
```

### Run Specific Test Category

```bash
# Health checks only
pytest tests/test_health_check.py -v

# Repository tests only
pytest tests/test_polymarket_repo.py -v

# Service tests only
pytest tests/test_web_crawler_service.py tests/test_message_service.py -v
```

### Run with Coverage

```bash
pytest tests/ --cov=. --cov-report=html --cov-report=term
```

Then open `htmlcov/index.html` in your browser for a detailed coverage report.

## Test Files

| File | Purpose |
|------|---------|
| `conftest.py` | Shared fixtures and test configuration |
| `test_polymarket_repo.py` | Tests for Polymarket scraping repository |
| `test_web_crawler_service.py` | Tests for web crawler service layer |
| `test_message_service.py` | Tests for message service |
| `test_health_check.py` | Health check tests for all services |

## Test Markers

- `@pytest.mark.asyncio` - Async tests
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests

## Mock Strategy

Tests use extensive mocking to avoid external dependencies:
- **Playwright**: Fully mocked to avoid browser launches
- **External APIs**: Mocked responses for deterministic testing
- **Database**: Not applicable (no database in this project)

## CI/CD Ready

All tests are designed to run in CI/CD environments:
- ✅ No external network calls
- ✅ No browser launches
- ✅ Fast execution
- ✅ Clear pass/fail reporting
