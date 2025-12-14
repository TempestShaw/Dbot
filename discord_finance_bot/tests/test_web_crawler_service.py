"""Tests for WebCrawlerService."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from services.web_crawler_service import WebCrawlerService
from repositories.web_crawler_repo import WebCrawlerRepo
from repositories.polymarket_repo import PolymarketRepo


class TestWebCrawlerService:
    """Test suite for WebCrawlerService."""

    def test_init(self, mock_config):
        """Test service initialization."""
        # Act
        service = WebCrawlerService(mock_config)

        # Assert
        assert isinstance(service.repo, WebCrawlerRepo)
        assert isinstance(service.polymarket_repo, PolymarketRepo)
        assert service.config == mock_config

    def test_get_top_sectors_names(self, mock_config, sample_sectors_data):
        """Test getting top sector names."""
        # Arrange
        service = WebCrawlerService(mock_config)
        service.repo.fetch_top_sectors_names = Mock(
            return_value=["Technology", "Healthcare"]
        )

        # Act
        result = service.get_top_sectors_names(limit=5)

        # Assert
        assert result == ["Technology", "Healthcare"]
        service.repo.fetch_top_sectors_names.assert_called_once_with(
            url=None, limit=5
        )

    def test_get_top_sectors_details(self, mock_config, sample_sectors_data):
        """Test getting top sector details."""
        # Arrange
        service = WebCrawlerService(mock_config)
        service.repo.fetch_top_sectors_details = Mock(
            return_value=sample_sectors_data
        )

        # Act
        result = service.get_top_sectors_details(limit=5)

        # Assert
        assert result == sample_sectors_data
        assert len(result) == 2
        assert result[0]['plateName'] == "Technology"

    @pytest.mark.asyncio
    async def test_get_top_sectors_details_async(
        self, mock_config, sample_sectors_data
    ):
        """Test async getting top sector details."""
        # Arrange
        service = WebCrawlerService(mock_config)
        service.repo.fetch_top_sectors_details_async = AsyncMock(
            return_value=sample_sectors_data
        )

        # Act
        result = await service.get_top_sectors_details_async(limit=10)

        # Assert
        assert result == sample_sectors_data
        service.repo.fetch_top_sectors_details_async.assert_called_once_with(
            url="https://www.moomoo.com/hans/quote/us/concepts", limit=10
        )

    @pytest.mark.asyncio
    async def test_get_polymarket_earnings_async(
        self, mock_config, sample_polymarket_data
    ):
        """Test getting Polymarket earnings data."""
        # Arrange
        service = WebCrawlerService(mock_config)
        service.polymarket_repo.scrape_polymarket_earnings = AsyncMock(
            return_value=sample_polymarket_data
        )

        # Act
        result = await service.get_polymarket_earnings_async()

        # Assert
        assert result == sample_polymarket_data
        assert len(result) == 3
        assert result[0]['ticker'] == "AAPL"
        assert result[0]['probability'] == "72%"

    @pytest.mark.asyncio
    async def test_get_polymarket_earnings_async_empty(
        self, mock_config
    ):
        """Test getting Polymarket earnings when no data available."""
        # Arrange
        service = WebCrawlerService(mock_config)
        service.polymarket_repo.scrape_polymarket_earnings = AsyncMock(
            return_value=[]
        )

        # Act
        result = await service.get_polymarket_earnings_async()

        # Assert
        assert result == []
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_get_polymarket_earnings_async_error(
        self, mock_config
    ):
        """Test error handling in get_polymarket_earnings_async."""
        # Arrange
        service = WebCrawlerService(mock_config)
        service.polymarket_repo.scrape_polymarket_earnings = AsyncMock(
            side_effect=Exception("Scraping failed")
        )

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await service.get_polymarket_earnings_async()

        assert "Scraping failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_top_sectors_details_async_error(
        self, mock_config
    ):
        """Test error handling in async sector details."""
        # Arrange
        service = WebCrawlerService(mock_config)
        service.repo.fetch_top_sectors_details_async = AsyncMock(
            side_effect=Exception("API error")
        )

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await service.get_top_sectors_details_async()

        assert "API error" in str(exc_info.value)

    def test_get_top_sectors_details_with_custom_url(
        self, mock_config, sample_sectors_data
    ):
        """Test getting sector details with custom URL."""
        # Arrange
        service = WebCrawlerService(mock_config)
        service.repo.fetch_top_sectors_details = Mock(
            return_value=sample_sectors_data
        )
        custom_url = "https://custom-url.com/sectors"

        # Act
        result = service.get_top_sectors_details(url=custom_url, limit=15)

        # Assert
        assert result == sample_sectors_data
        service.repo.fetch_top_sectors_details.assert_called_once_with(
            url=custom_url, limit=15
        )

    @pytest.mark.asyncio
    async def test_get_top_sectors_details_async_with_custom_url(
        self, mock_config, sample_sectors_data
    ):
        """Test async sector details with custom URL."""
        # Arrange
        service = WebCrawlerService(mock_config)
        service.repo.fetch_top_sectors_details_async = AsyncMock(
            return_value=sample_sectors_data
        )
        custom_url = "https://custom-url.com/sectors"

        # Act
        result = await service.get_top_sectors_details_async(
            url=custom_url, limit=20
        )

        # Assert
        assert result == sample_sectors_data
        service.repo.fetch_top_sectors_details_async.assert_called_once_with(
            url=custom_url, limit=20
        )

    def test_get_top_sectors_names_with_custom_url(self, mock_config):
        """Test getting sector names with custom URL."""
        # Arrange
        service = WebCrawlerService(mock_config)
        service.repo.fetch_top_sectors_names = Mock(return_value=["Tech"])
        custom_url = "https://custom-url.com/names"

        # Act
        result = service.get_top_sectors_names(url=custom_url)

        # Assert
        assert result == ["Tech"]
        service.repo.fetch_top_sectors_names.assert_called_once_with(
            url=custom_url, limit=5
        )
