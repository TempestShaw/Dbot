"""Pytest configuration and shared fixtures."""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from config import Config


@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    return Config(
        discord_token="test_token",
        channel_id=123456789,
        selected_stocks=["AAPL", "MSFT", "GOOGL"],
        timezone="Asia/Shanghai",
        alphavantage_api_key="test_api_key"
    )


@pytest.fixture
def sample_polymarket_data():
    """Sample Polymarket earnings data for testing."""
    return [
        {
            "date": "16",
            "time": "Pre Market",
            "ticker": "AAPL",
            "eps_forecast": "EPS $2.10",
            "probability": "72%"
        },
        {
            "date": "16",
            "time": "Post Market",
            "ticker": "MSFT",
            "eps_forecast": "EPS $3.25",
            "probability": "68%"
        },
        {
            "date": "17",
            "time": "Pre Market",
            "ticker": "GOOGL",
            "eps_forecast": "EPS $1.85",
            "probability": "75%"
        }
    ]


@pytest.fixture
def sample_sectors_data():
    """Sample sectors data for testing."""
    return [
        {
            "plateName": "Technology",
            "plateEnName": "Technology",
            "plateCode": "TECH",
            "stockName": "AAPL",
            "stockCode": "AAPL",
            "changeRatio": "+2.5%",
            "stockChangeRatio": "+3.2%",
            "priceRiseCount": 45,
            "priceFallCount": 12,
            "priceSameCount": 3,
            "tradeTurnover": "125.6B",
            "tradeVolumn": "89.2M",
            "backgroundImageUrl": ""
        },
        {
            "plateName": "Healthcare",
            "plateEnName": "Healthcare",
            "plateCode": "HEALTH",
            "stockName": "JNJ",
            "stockCode": "JNJ",
            "changeRatio": "+1.8%",
            "stockChangeRatio": "+2.1%",
            "priceRiseCount": 32,
            "priceFallCount": 15,
            "priceSameCount": 8,
            "tradeTurnover": "89.3B",
            "tradeVolumn": "56.7M",
            "backgroundImageUrl": ""
        }
    ]


@pytest.fixture
def sample_earnings_data():
    """Sample earnings data for testing."""
    return [
        {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "reportDate": "2025-01-16",
            "estimateEPS": "2.10",
            "estimateCurrency": "USD"
        },
        {
            "symbol": "MSFT",
            "name": "Microsoft Corp.",
            "reportDate": "2025-01-16",
            "estimateEPS": "3.25",
            "estimateCurrency": "USD"
        }
    ]


@pytest.fixture
def sample_ipos_data():
    """Sample IPOs data for testing."""
    return [
        {
            "symbol": "NEWCO",
            "name": "New Company Inc.",
            "ipoDate": "2025-01-20",
            "priceRange": "$15-17",
            "currency": "USD"
        }
    ]


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_playwright():
    """Mock Playwright for testing."""
    with patch('repositories.polymarket_repo.async_playwright') as mock:
        mock_playwright_instance = AsyncMock()
        mock_context = AsyncMock()
        mock_browser = AsyncMock()
        mock_page = AsyncMock()

        mock_playwright_instance.return_value.__aenter__.return_value = mock_playwright_instance
        mock_playwright_instance.return_value.__aexit__.return_value = None
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page

        yield {
            'playwright': mock,
            'browser': mock_browser,
            'page': mock_page,
            'context': mock_context
        }


@pytest.fixture
def mock_alphavantage_service():
    """Mock AlphaVantage service for testing."""
    mock_service = Mock()
    mock_service.get_week_earnings_for_dates = Mock(return_value=[])
    mock_service.get_week_ipos_for_dates = Mock(return_value=[])
    return mock_service


@pytest.fixture
def mock_web_crawler_repo():
    """Mock WebCrawlerRepo for testing."""
    mock_repo = Mock()
    mock_repo.fetch_top_sectors_details_async = AsyncMock(return_value=[])
    return mock_repo


@pytest.fixture
def mock_polymarket_repo():
    """Mock PolymarketRepo for testing."""
    mock_repo = AsyncMock()
    return mock_repo
