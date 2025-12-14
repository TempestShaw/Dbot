# Testing Guide

## Overview

This project includes a comprehensive test suite for the Discord Finance Bot, including unit tests, integration tests, and health checks.

## Test Structure

```
tests/
├── __init__.py              # Tests package initialization
├── conftest.py              # Pytest configuration and fixtures
├── test_polymarket_repo.py  # Tests for Polymarket scraping
├── test_web_crawler_service.py  # Tests for web crawler service
├── test_message_service.py  # Tests for message service
└── test_health_check.py     # Health check tests
```

## Running Tests

### Method 1: Using the Test Runner Script (Recommended)

```bash
./run_tests.sh
```

This script will:
1. Check if pytest is installed
2. Install dependencies if needed
3. Run all tests with verbose output

### Method 2: Using pytest Directly

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_polymarket_repo.py -v

# Run tests matching a pattern
pytest tests/ -k "polymarket" -v

# Run tests without asyncio warnings
pytest tests/ -v --disable-warnings
```

### Method 3: Using IDE Integration

Most IDEs (VS Code, PyCharm) have built-in pytest integration:

1. **VS Code**: Install the Python extension and use the Test Explorer
2. **PyCharm**: Right-click on test directory and select "Run pytest in tests"

## Test Categories

### 1. Unit Tests

Focus on testing individual components in isolation:

```bash
# Run only unit tests
pytest tests/ -m unit -v
```

### 2. Integration Tests

Test the interaction between components:

```bash
# Run only integration tests
pytest tests/ -m integration -v
```

### 3. Health Check Tests

Verify that all services are properly configured and functional:

```bash
# Run only health checks
pytest tests/test_health_check.py -v
```

### 4. Async Tests

All async tests are properly configured with pytest-asyncio:

```bash
# Run only async tests
pytest tests/ -m asyncio -v
```

## Test Fixtures

The `conftest.py` file provides several useful fixtures:

- `mock_config`: Mock configuration for testing
- `sample_polymarket_data`: Sample Polymarket earnings data
- `sample_sectors_data`: Sample sectors data
- `sample_earnings_data`: Sample earnings data
- `sample_ipos_data`: Sample IPOs data
- `mock_playwright`: Mocked Playwright for testing scrapers
- `event_loop`: Async event loop for testing

## Coverage Reports

To generate a coverage report:

```bash
pytest tests/ --cov=repositories --cov=services --cov=controllers --cov-report=html
```

Then open `htmlcov/index.html` in your browser.

## Mocking

Tests use extensive mocking to avoid external dependencies:

### Playwright Mocking

```python
@pytest.mark.asyncio
async def test_scrape_polymarket_earnings_success(self, mock_config, mock_playwright):
    mock_page = mock_playwright['page']
    # Mock page interactions...
    result = await repo.scrape_polymarket_earnings()
```

### API Service Mocking

```python
service.alpha_service.get_week_earnings_for_dates = Mock(return_value=[])
```

## Test Data

All test data is defined in `conftest.py` to ensure consistency across tests.

## Continuous Integration

The test suite is designed to run in CI/CD environments:

- No external API calls (everything is mocked)
- No browser interaction (Playwright is mocked)
- Fast execution
- Clear pass/fail reporting

## Adding New Tests

### Writing a New Test File

1. Create a new file in the `tests/` directory
2. Name it `test_<module_name>.py`
3. Import necessary modules and fixtures
4. Write test methods with the `test_` prefix

Example:

```python
import pytest
from services.web_crawler_service import WebCrawlerService

class TestWebCrawlerService:
    def test_new_feature(self, mock_config):
        service = WebCrawlerService(mock_config)
        # Test implementation
        assert True
```

### Marking Tests

Use markers to categorize tests:

```python
@pytest.mark.unit
def test_unit_feature():
    pass

@pytest.mark.integration
@pytest.mark.asyncio
async def test_integration_feature():
    pass
```

## Debugging Failed Tests

### Increase Verbosity

```bash
pytest tests/ -vvv --tb=long
```

### Run a Specific Test

```bash
pytest tests/test_polymarket_repo.py::TestPolymarketRepo::test_scrape_polymarket_earnings_success -v
```

### Drop into Debugger on Failure

```bash
pytest tests/ --pdb
```

## Best Practices

1. **Keep tests independent**: Each test should run in isolation
2. **Use descriptive names**: Test names should describe what they're testing
3. **Mock external dependencies**: Don't make real API calls in tests
4. **Test edge cases**: Include tests for error conditions
5. **Keep tests fast**: Unit tests should run in milliseconds

## Troubleshooting

### Issue: "ModuleNotFoundError"

**Solution**: Run tests from the project root directory:

```bash
cd /Users/a123/Projects/Others/Dbot/discord_finance_bot
pytest tests/ -v
```

### Issue: "RuntimeError: Event loop is closed"

**Solution**: Ensure async tests use `@pytest.mark.asyncio` and event_loop fixture

### Issue: "Playwright not installed"

**Solution**: Mock is used in tests, so this shouldn't happen. If it does, check the mock setup in `conftest.py`.

## Coverage Goals

- **Repository layer**: > 90%
- **Service layer**: > 85%
- **Controller layer**: > 80%

Current coverage is tracked in CI and reported in pull requests.
