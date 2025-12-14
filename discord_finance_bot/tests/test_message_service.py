"""Tests for MessageService."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from services.message_service import MessageService
import datetime as dt
from zoneinfo import ZoneInfo


class TestMessageService:
    """Test suite for MessageService."""

    def test_init(self, mock_config):
        """Test service initialization."""
        # Act
        service = MessageService(mock_config)

        # Assert
        assert service.config == mock_config
        assert service.alpha_service is not None
        assert service.web_crawler_service is not None

    def test_generate_daily_summary_json(
        self, mock_config, sample_sectors_data, sample_earnings_data, sample_ipos_data
    ):
        """Test synchronous daily summary JSON generation."""
        # Arrange
        service = MessageService(mock_config)
        service.web_crawler_service.get_top_sectors_details = Mock(
            return_value=sample_sectors_data
        )
        service.alpha_service.get_week_earnings_for_dates = Mock(
            return_value=sample_earnings_data
        )
        service.alpha_service.get_week_ipos_for_dates = Mock(
            return_value=sample_ipos_data
        )

        # Act
        result = service.generate_daily_summary_json()

        # Assert
        assert 'top_sectors_details' in result
        assert 'earnings' in result
        assert 'polymarket_earnings' in result
        assert 'ipos' in result
        assert 'dates' in result

        assert len(result['top_sectors_details']) == 2
        assert result['top_sectors_details'][0]['plateName'] == "Technology"
        assert result['earnings'] == sample_earnings_data
        assert result['polymarket_earnings'] == []
        assert result['ipos'] == sample_ipos_data
        assert len(result['dates']) == 3

    @pytest.mark.asyncio
    async def test_generate_daily_summary_json_async(
        self, mock_config, sample_sectors_data, sample_earnings_data,
        sample_ipos_data, sample_polymarket_data
    ):
        """Test async daily summary JSON generation with Polymarket data."""
        # Arrange
        service = MessageService(mock_config)
        service.web_crawler_service.get_top_sectors_details_async = AsyncMock(
            return_value=sample_sectors_data
        )
        service.web_crawler_service.get_polymarket_earnings_async = AsyncMock(
            return_value=sample_polymarket_data
        )
        service.alpha_service.get_week_earnings_for_dates = Mock(
            return_value=sample_earnings_data
        )
        service.alpha_service.get_week_ipos_for_dates = Mock(
            return_value=sample_ipos_data
        )

        # Act
        result = await service.generate_daily_summary_json_async()

        # Assert
        assert 'top_sectors_details' in result
        assert 'earnings' in result
        assert 'polymarket_earnings' in result
        assert 'ipos' in result
        assert 'dates' in result

        assert len(result['polymarket_earnings']) == 3
        assert result['polymarket_earnings'][0]['ticker'] == "AAPL"
        assert result['polymarket_earnings'][0]['probability'] == "72%"

    @pytest.mark.asyncio
    async def test_generate_daily_summary_json_async_no_polymarket_data(
        self, mock_config, sample_sectors_data, sample_earnings_data, sample_ipos_data
    ):
        """Test async summary when Polymarket returns no data."""
        # Arrange
        service = MessageService(mock_config)
        service.web_crawler_service.get_top_sectors_details_async = AsyncMock(
            return_value=sample_sectors_data
        )
        service.web_crawler_service.get_polymarket_earnings_async = AsyncMock(
            return_value=[]
        )
        service.alpha_service.get_week_earnings_for_dates = Mock(
            return_value=sample_earnings_data
        )
        service.alpha_service.get_week_ipos_for_dates = Mock(
            return_value=sample_ipos_data
        )

        # Act
        result = await service.generate_daily_summary_json_async()

        # Assert
        assert result['polymarket_earnings'] == []
        assert len(result) == 5  # All expected keys present

    def test_generate_daily_summary_text(
        self, mock_config, sample_sectors_data, sample_earnings_data, sample_ipos_data
    ):
        """Test synchronous text summary generation."""
        # Arrange
        service = MessageService(mock_config)
        service.web_crawler_service.get_top_sectors_details = Mock(
            return_value=sample_sectors_data
        )
        service.alpha_service.get_week_earnings_for_dates = Mock(
            return_value=sample_earnings_data
        )
        service.alpha_service.get_week_ipos_for_dates = Mock(
            return_value=sample_ipos_data
        )

        # Act
        result = service.generate_daily_summary_text()

        # Assert
        assert isinstance(result, str)
        assert "Top Sector Details" in result
        assert "Earnings & IPOs" in result
        assert "Earnings" in result
        assert "IPOs" in result

    @pytest.mark.asyncio
    async def test_generate_daily_summary_text_async(
        self, mock_config, sample_sectors_data, sample_earnings_data,
        sample_ipos_data, sample_polymarket_data
    ):
        """Test async text summary generation with Polymarket data."""
        # Arrange
        service = MessageService(mock_config)
        service.web_crawler_service.get_top_sectors_details_async = AsyncMock(
            return_value=sample_sectors_data
        )
        service.web_crawler_service.get_polymarket_earnings_async = AsyncMock(
            return_value=sample_polymarket_data
        )
        service.alpha_service.get_week_earnings_for_dates = Mock(
            return_value=sample_earnings_data
        )
        service.alpha_service.get_week_ipos_for_dates = Mock(
            return_value=sample_ipos_data
        )

        # Act
        result = await service.generate_daily_summary_text_async()

        # Assert
        assert isinstance(result, str)
        assert "Top Sector Details" in result
        assert "Earnings & IPOs" in result

    @pytest.mark.asyncio
    async def test_generate_daily_summary_json_async_error_handling(
        self, mock_config
    ):
        """Test error handling in async JSON generation."""
        # Arrange
        service = MessageService(mock_config)
        service.web_crawler_service.get_top_sectors_details_async = AsyncMock(
            side_effect=Exception("Service error")
        )

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await service.generate_daily_summary_json_async()

        assert "Service error" in str(exc_info.value)

    def test_generate_daily_summary_json_empty_data(self, mock_config):
        """Test summary generation with empty data."""
        # Arrange
        service = MessageService(mock_config)
        service.web_crawler_service.get_top_sectors_details = Mock(return_value=[])
        service.alpha_service.get_week_earnings_for_dates = Mock(return_value=[])
        service.alpha_service.get_week_ipos_for_dates = Mock(return_value=[])

        # Act
        result = service.generate_daily_summary_json()

        # Assert
        assert result['top_sectors_details'] == []
        assert result['earnings'] == []
        assert result['polymarket_earnings'] == []
        assert result['ipos'] == []
        assert len(result['dates']) == 3

    @pytest.mark.asyncio
    async def test_generate_daily_summary_json_async_empty_data(
        self, mock_config
    ):
        """Test async summary generation with empty data."""
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
        result = await service.generate_daily_summary_json_async()

        # Assert
        assert result['top_sectors_details'] == []
        assert result['earnings'] == []
        assert result['polymarket_earnings'] == []
        assert result['ipos'] == []

    def test_summary_dates_format(self, mock_config):
        """Test that dates are properly formatted in summary."""
        # Arrange
        service = MessageService(mock_config)
        service.web_crawler_service.get_top_sectors_details = Mock(return_value=[])
        service.alpha_service.get_week_earnings_for_dates = Mock(return_value=[])
        service.alpha_service.get_week_ipos_for_dates = Mock(return_value=[])

        # Act
        result = service.generate_daily_summary_json()

        # Assert
        dates = result['dates']
        assert len(dates) == 3
        # Verify dates are ISO formatted strings
        for date_str in dates:
            assert isinstance(date_str, str)
            # Should be YYYY-MM-DD format
            assert len(date_str) == 10
            assert '-' in date_str

    @pytest.mark.asyncio
    async def test_polymarket_data_integration(
        self, mock_config, sample_polymarket_data
    ):
        """Test that Polymarket data is properly integrated."""
        # Arrange
        service = MessageService(mock_config)
        service.web_crawler_service.get_top_sectors_details_async = AsyncMock(
            return_value=[]
        )
        service.web_crawler_service.get_polymarket_earnings_async = AsyncMock(
            return_value=sample_polymarket_data
        )
        service.alpha_service.get_week_earnings_for_dates = Mock(return_value=[])
        service.alpha_service.get_week_ipos_for_dates = Mock(return_value=[])

        # Act
        result = await service.generate_daily_summary_json_async()

        # Assert
        polymarket_data = result['polymarket_earnings']
        assert len(polymarket_data) == 3
        assert polymarket_data[0]['date'] == "16"
        assert polymarket_data[0]['time'] == "Pre Market"
        assert polymarket_data[0]['ticker'] == "AAPL"
        assert polymarket_data[0]['eps_forecast'] == "EPS $2.10"
        assert polymarket_data[0]['probability'] == "72%"
