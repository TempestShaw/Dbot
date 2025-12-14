"""Health check tests for all services."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from services.web_crawler_service import WebCrawlerService
from services.message_service import MessageService
from repositories.polymarket_repo import PolymarketRepo
from repositories.web_crawler_repo import WebCrawlerRepo


class TestHealthCheck:
    """Health check tests for crawling and API services."""

    def test_polymarket_repo_health(self, mock_config):
        """Test that PolymarketRepo can be instantiated."""
        # Act
        repo = PolymarketRepo(mock_config)

        # Assert
        assert repo is not None
        assert repo.config == mock_config
        assert repo.logger is not None

    def test_web_crawler_repo_health(self, mock_config):
        """Test that WebCrawlerRepo can be instantiated."""
        # Act
        repo = WebCrawlerRepo(mock_config)

        # Assert
        assert repo is not None
        assert repo.config == mock_config
        assert repo.logger is not None

    def test_web_crawler_service_health(self, mock_config):
        """Test that WebCrawlerService can be instantiated."""
        # Act
        service = WebCrawlerService(mock_config)

        # Assert
        assert service is not None
        assert service.config == mock_config
        assert service.repo is not None
        assert service.polymarket_repo is not None

    def test_message_service_health(self, mock_config):
        """Test that MessageService can be instantiated."""
        # Act
        service = MessageService(mock_config)

        # Assert
        assert service is not None
        assert service.config == mock_config
        assert service.alpha_service is not None
        assert service.web_crawler_service is not None

    @pytest.mark.asyncio
    async def test_polymarket_scraper_health_with_mock(
        self, mock_config, mock_playwright
    ):
        """Test Polymarket scraper health with mocked Playwright."""
        # Arrange
        repo = PolymarketRepo(mock_config)
        mock_page = mock_playwright['page']

        # Mock successful scraping
        mock_page.locator.return_value.all = AsyncMock(return_value=[])
        mock_page.wait_for_selector = AsyncMock()
        mock_page.wait_for_timeout = AsyncMock()

        # Act
        result = await repo.scrape_polymarket_earnings()

        # Assert
        assert isinstance(result, list)
        assert result == []  # Empty because we mocked no data

    @pytest.mark.asyncio
    async def test_polymarket_scraper_no_playwright(self, mock_config):
        """Test Polymarket scraper when Playwright is not installed."""
        # Arrange
        repo = PolymarketRepo(mock_config)

        with patch('repositories.polymarket_repo.async_playwright', None):
            # Act
            result = await repo.scrape_polymarket_earnings()

            # Assert
            assert result == []
            assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_web_crawler_service_async_health(self, mock_config):
        """Test WebCrawlerService async methods health."""
        # Arrange
        service = WebCrawlerService(mock_config)
        service.repo.fetch_top_sectors_details_async = AsyncMock(return_value=[])
        service.polymarket_repo.scrape_polymarket_earnings = AsyncMock(return_value=[])

        # Act
        sectors = await service.get_top_sectors_details_async()
        earnings = await service.get_polymarket_earnings_async()

        # Assert
        assert isinstance(sectors, list)
        assert isinstance(earnings, list)

    def test_web_crawler_service_sync_health(self, mock_config):
        """Test WebCrawlerService sync methods health."""
        # Arrange
        service = WebCrawlerService(mock_config)
        service.repo.fetch_top_sectors_details = Mock(return_value=[])
        service.repo.fetch_top_sectors_names = Mock(return_value=[])

        # Act
        sectors = service.get_top_sectors_details()
        names = service.get_top_sectors_names()

        # Assert
        assert isinstance(sectors, list)
        assert isinstance(names, list)

    @pytest.mark.asyncio
    async def test_message_service_async_health(self, mock_config):
        """Test MessageService async methods health."""
        # Arrange
        service = MessageService(mock_config)
        service.web_crawler_service.get_top_sectors_details_async = AsyncMock(
            return_value=[]
        )
        service.web_crawler_service.get_polymarket_earnings_async = AsyncMock(
            return_value=[]
        )
        service.alpha_service.get_week_earnings_for_dates = Mock(return_value=[])
        service.alpha_service.get_week_ipos_for_dates = Mock(return_value=[])

        # Act
        summary = await service.generate_daily_summary_json_async()
        text = await service.generate_daily_summary_text_async()

        # Assert
        assert isinstance(summary, dict)
        assert 'top_sectors_details' in summary
        assert 'polymarket_earnings' in summary
        assert isinstance(text, str)

    def test_message_service_sync_health(self, mock_config):
        """Test MessageService sync methods health."""
        # Arrange
        service = MessageService(mock_config)
        service.web_crawler_service.get_top_sectors_details = Mock(return_value=[])
        service.alpha_service.get_week_earnings_for_dates = Mock(return_value=[])
        service.alpha_service.get_week_ipos_for_dates = Mock(return_value=[])

        # Act
        summary = service.generate_daily_summary_json()
        text = service.generate_daily_summary_text()

        # Assert
        assert isinstance(summary, dict)
        assert 'top_sectors_details' in summary
        assert isinstance(text, str)

    @pytest.mark.asyncio
    async def test_full_pipeline_health(self, mock_config):
        """Test full pipeline health with mocked dependencies."""
        # Arrange
        web_service = WebCrawlerService(mock_config)
        message_service = MessageService(mock_config)

        web_service.repo.fetch_top_sectors_details_async = AsyncMock(
            return_value=[]
        )
        web_service.polymarket_repo.scrape_polymarket_earnings = AsyncMock(
            return_value=[]
        )
        message_service.alpha_service.get_week_earnings_for_dates = Mock(
            return_value=[]
        )
        message_service.alpha_service.get_week_ipos_for_dates = Mock(
            return_value=[]
        )

        # Act
        polymarket_data = await web_service.get_polymarket_earnings_async()
        sectors = await web_service.get_top_sectors_details_async()
        summary = await message_service.generate_daily_summary_json_async()

        # Assert
        assert isinstance(polymarket_data, list)
        assert isinstance(sectors, list)
        assert isinstance(summary, dict)
        assert 'polymarket_earnings' in summary

    @pytest.mark.asyncio
    async def test_error_recovery_health(self, mock_config):
        """Test that services handle errors gracefully."""
        # Arrange
        service = WebCrawlerService(mock_config)
        service.polymarket_repo.scrape_polymarket_earnings = AsyncMock(
            side_effect=Exception("Network error")
        )

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await service.get_polymarket_earnings_async()

        assert "Network error" in str(exc_info.value)

    def test_service_dependencies(self, mock_config):
        """Test that services properly initialize their dependencies."""
        # Act
        web_service = WebCrawlerService(mock_config)
        message_service = MessageService(mock_config)

        # Assert - Check dependency injection
        assert hasattr(web_service, 'repo')
        assert hasattr(web_service, 'polymarket_repo')
        assert hasattr(message_service, 'alpha_service')
        assert hasattr(message_service, 'web_crawler_service')

        # Check that repos are properly instantiated
        assert isinstance(web_service.repo, WebCrawlerRepo)
        assert isinstance(web_service.polymarket_repo, PolymarketRepo)
