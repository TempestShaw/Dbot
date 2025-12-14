"""Tests for PolymarketRepo."""

import pytest
from unittest.mock import AsyncMock, patch
from repositories.polymarket_repo import PolymarketRepo


class TestPolymarketRepo:
    """Test suite for PolymarketRepo."""

    @pytest.mark.asyncio
    async def test_scrape_polymarket_earnings_success(
        self, mock_config, mock_playwright, sample_polymarket_data
    ):
        """Test successful scraping of Polymarket earnings."""
        # Arrange
        repo = PolymarketRepo(mock_config)
        mock_page = mock_playwright['page']

        # Mock the page elements
        mock_active_column = AsyncMock()
        mock_active_column.locator = AsyncMock()
        mock_active_column.locator.return_value.first = AsyncMock()
        mock_active_column.locator.return_value.first.count = AsyncMock(return_value=1)
        mock_active_column.locator.return_value.first.inner_text = AsyncMock(
            return_value="16"
        )
        mock_active_column.locator.return_value.all = AsyncMock(
            return_value=[mock_active_column]
        )

        mock_group = AsyncMock()
        mock_group.locator = AsyncMock()
        mock_group.locator.return_value.all = AsyncMock(return_value=[mock_group])

        mock_time_element = AsyncMock()
        mock_time_element.inner_text = AsyncMock(return_value="Pre Market")
        mock_group.locator.return_value.first.inner_text = AsyncMock(
            return_value="Pre Market"
        )

        mock_card = AsyncMock()
        mock_card.locator = AsyncMock()
        mock_card.locator.return_value.inner_text = AsyncMock(side_effect=[
            "AAPL",  # ticker
            "EPS $2.10",  # eps_forecast
            "72%"  # probability
        ])
        mock_group.locator.return_value.all = AsyncMock(return_value=[mock_card])
        mock_active_column.locator.return_value.all = AsyncMock(return_value=[mock_group])

        mock_page.locator = AsyncMock()
        mock_page.locator.return_value.all = AsyncMock(
            return_value=[mock_active_column]
        )
        mock_page.wait_for_selector = AsyncMock()
        mock_page.wait_for_timeout = AsyncMock()

        # Act
        result = await repo.scrape_polymarket_earnings()

        # Assert
        assert len(result) > 0
        assert isinstance(result, list)
        assert all(isinstance(item, dict) for item in result)
        assert all(
            'date' in item and 'time' in item and 'ticker' in item
            for item in result
        )

    @pytest.mark.asyncio
    async def test_scrape_polymarket_earnings_no_playwright(self, mock_config):
        """Test behavior when Playwright is not installed."""
        # Arrange
        repo = PolymarketRepo(mock_config)

        with patch('repositories.polymarket_repo.async_playwright', None):
            # Act
            result = await repo.scrape_polymarket_earnings()

            # Assert
            assert result == []

    @pytest.mark.asyncio
    async def test_scrape_polymarket_earnings_timeout(
        self, mock_config, mock_playwright
    ):
        """Test handling of page load timeout."""
        # Arrange
        repo = PolymarketRepo(mock_config)
        mock_page = mock_playwright['page']
        mock_page.wait_for_selector = AsyncMock(
            side_effect=Exception("Timeout")
        )

        # Act
        result = await repo.scrape_polymarket_earnings()

        # Assert
        assert result == []

    @pytest.mark.asyncio
    async def test_scrape_polymarket_earnings_no_data(
        self, mock_config, mock_playwright
    ):
        """Test when no earnings data is found."""
        # Arrange
        repo = PolymarketRepo(mock_config)
        mock_page = mock_playwright['page']

        # Mock empty results
        mock_page.locator.return_value.all = AsyncMock(return_value=[])
        mock_page.wait_for_selector = AsyncMock()
        mock_page.wait_for_timeout = AsyncMock()

        # Act
        result = await repo.scrape_polymarket_earnings()

        # Assert
        assert result == []

    @pytest.mark.asyncio
    async def test_scrape_polymarket_earnings_partial_data(
        self, mock_config, mock_playwright
    ):
        """Test when some cards have incomplete data."""
        # Arrange
        repo = PolymarketRepo(mock_config)
        mock_page = mock_playwright['page']

        # Create mock with some failing elements
        mock_active_column = AsyncMock()
        mock_active_column.locator = AsyncMock()
        mock_active_column.locator.return_value.first = AsyncMock()
        mock_active_column.locator.return_value.first.count = AsyncMock(
            return_value=0
        )  # Will trigger fallback
        mock_active_column.locator.return_value.all = AsyncMock(return_value=[])

        mock_page.locator.return_value.all = AsyncMock(
            return_value=[mock_active_column]
        )
        mock_page.wait_for_selector = AsyncMock()
        mock_page.wait_for_timeout = AsyncMock()

        # Act
        result = await repo.scrape_polymarket_earnings()

        # Assert
        # Should handle gracefully and return empty or partial results
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_scrape_polymarket_earnings_exception_handling(
        self, mock_config, mock_playwright
    ):
        """Test exception handling during scraping."""
        # Arrange
        repo = PolymarketRepo(mock_config)
        mock_page = mock_playwright['page']
        mock_page.goto = AsyncMock(side_effect=Exception("Network error"))

        # Act
        result = await repo.scrape_polymarket_earnings()

        # Assert
        assert result == []

    def test_init(self, mock_config):
        """Test repository initialization."""
        # Act
        repo = PolymarketRepo(mock_config)

        # Assert
        assert repo.config == mock_config
        assert repo.logger is not None

    @pytest.mark.asyncio
    async def test_scrape_polymarket_earnings_multiple_columns(
        self, mock_config, mock_playwright
    ):
        """Test scraping with multiple date columns."""
        # Arrange
        repo = PolymarketRepo(mock_config)
        mock_page = mock_playwright['page']

        # Create multiple columns
        columns = []
        for i in range(3):
            col = AsyncMock()
            col.locator = AsyncMock()
            col.locator.return_value.first = AsyncMock()
            col.locator.return_value.first.count = AsyncMock(return_value=1)
            col.locator.return_value.first.inner_text = AsyncMock(
                return_value=str(16 + i)
            )
            col.locator.return_value.all = AsyncMock(return_value=[])
            columns.append(col)

        mock_page.locator.return_value.all = AsyncMock(return_value=columns)
        mock_page.wait_for_selector = AsyncMock()
        mock_page.wait_for_timeout = AsyncMock()

        # Act
        result = await repo.scrape_polymarket_earnings()

        # Assert
        assert isinstance(result, list)
