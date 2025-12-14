"""
Daily Summary Service - Handles daily summary generation and Discord messaging.

This service is responsible for:
1. Generating daily market summary data
2. Formatting the data into professional Discord embeds
3. Generating sector performance charts
4. Sending messages to Discord channels

The scheduler simply calls this service without knowing the implementation details.
"""

import asyncio
import discord
import io
from typing import Optional
from utils.logger import get_logger
from services.market_data_aggregator import MarketDataAggregator
from services.message_service import MessageService
from zoneinfo import ZoneInfo
import datetime as dt


class DailySummaryService:
    """Service for generating and sending daily market summaries."""

    def __init__(self, bot, config):
        self.bot = bot
        self.config = config
        self.logger = get_logger(__name__)
        self.market_data = MarketDataAggregator(config)
        self.message_service = MessageService(config)

    async def send_daily_summary(self) -> None:
        """Generate and send daily market summary to Discord."""
        try:
            self.logger.info("Generating daily market summary...")

            # Generate summary data
            summary_data = await self._generate_summary_data()

            # Build Discord embed
            embed = self._build_professional_embed(summary_data)

            # Generate and attach sector performance chart
            chart_file = None
            if summary_data.get("top_sectors_details"):
                self.logger.info("Generating sector performance chart...")
                chart_image = self.market_data.generate_sector_chart(
                    summary_data["top_sectors_details"]
                )
                if chart_image:
                    chart_file = discord.File(io.BytesIO(chart_image), filename="sector_chart.png")
                    embed.set_image(url="attachment://sector_chart.png")

            # Send to Discord
            await self._send_embed_to_channel(embed, chart_file)

            self.logger.info("Daily market summary sent successfully")

        except Exception as e:
            self.logger.error(f"Failed to send daily summary: {e}")
            raise

    async def _generate_summary_data(self) -> dict:
        """Generate summary data from all sources."""
        # Get current date
        today = dt.datetime.now(ZoneInfo(self.config.timezone)).date()
        dates = [today, today + dt.timedelta(days=1), today + dt.timedelta(days=2)]

        # Use MessageService to get complete data
        json_data = await self.message_service.generate_daily_summary_json_async()

        # Add dates to the data
        json_data['dates'] = [d.isoformat() for d in dates]

        return json_data

    async def _send_embed_to_channel(self, embed: discord.Embed, chart_file: Optional[discord.File] = None) -> None:
        """Send embed to the configured Discord channel."""
        channel_id = self.config.channel_id

        if not channel_id:
            self.logger.warning("DISCORD_CHANNEL_ID not configured; logging summary instead.")
            # For testing, just log the summary
            self.logger.info("Daily summary (logged mode):\n" + embed.description)
            return

        channel = self.bot.get_channel(channel_id)

        if not channel:
            self.logger.warning(f"Channel {channel_id} not found; ensure bot has access.")
            return

        try:
            if chart_file:
                await channel.send(embed=embed, files=[chart_file])
                self.logger.info(f"Embed with chart sent to channel {channel_id}")
            else:
                await channel.send(embed=embed)
                self.logger.info(f"Embed sent to channel {channel_id}")
        except Exception as e:
            self.logger.error(f"Failed to send embed to channel {channel_id}: {e}")
            raise

    def _build_professional_embed(self, data: dict) -> discord.Embed:
        """Build professional embed with structured sections."""
        # Get data from different sources
        polymarket_earnings = data.get("polymarket_earnings", [])
        sectors = data.get("top_sectors_details", [])
        earnings = data.get("earnings", [])
        ipos = data.get("ipos", [])
        dates = data.get("dates", [])

        # Create main embed
        date_str = dates[-1] if dates else "Today"
        embed = discord.Embed(
            title="Daily Market Summary",
            description=f"Comprehensive market analysis for {date_str}",
            color=0x3498db,  # Professional blue
            url="https://polymarket.com/earnings"
        )

        # Set professional branding
        embed.set_author(
            name="Market Intelligence System",
            icon_url="https://img.icons8.com/color/48/line-chart.png"
        )

        # === SECTION 1: POLYMARKET EARNINGS PREDICTIONS ===
        if polymarket_earnings:
            embed.add_field(
                name="Market Predictions (Polymarket)",
                value="Earnings forecasts with confidence levels from prediction markets",
                inline=False
            )

            # Group by confidence level
            high_conf = [e for e in polymarket_earnings if self._get_confidence_level(e.get('probability', '0%')) == "High"]
            med_conf = [e for e in polymarket_earnings if self._get_confidence_level(e.get('probability', '0%')) == "Medium"]
            low_conf = [e for e in polymarket_earnings if self._get_confidence_level(e.get('probability', '0%')) == "Low"]

            # High confidence section
            if high_conf:
                embed.add_field(
                    name="High Confidence (≥70%)",
                    value=self._format_polymarket_section(high_conf[:5]),
                    inline=False
                )

            # Medium confidence section
            if med_conf:
                embed.add_field(
                    name="Medium Confidence (50-70%)",
                    value=self._format_polymarket_section(med_conf[:5]),
                    inline=True
                )

            # Low confidence section
            if low_conf:
                embed.add_field(
                    name="Low Confidence (<50%)",
                    value=self._format_polymarket_section(low_conf[:5]),
                    inline=True
                )

        # === SECTION 2: TOP MARKET SECTORS ===
        if sectors:
            embed.add_field(
                name="Top Market Sectors (Moomoo)",
                value="Leading sectors with performance metrics",
                inline=False
            )

            sectors_text = self._format_sectors_table(sectors[:10])  # Show top 10
            embed.add_field(
                name="Sector Performance (Top 10)",
                value=sectors_text,
                inline=False
            )

        # === SECTION 3: EARNINGS CALENDAR ===
        if earnings:
            embed.add_field(
                name="Upcoming Earnings (Alpha Vantage)",
                value="Official earnings reports scheduled",
                inline=False
            )

            earnings_text = self._format_earnings(earnings[:5])
            embed.add_field(
                name="Earnings Schedule",
                value=earnings_text,
                inline=False
            )

        # === SECTION 4: IPO CALENDAR ===
        if ipos:
            embed.add_field(
                name="Upcoming IPOs (Alpha Vantage)",
                value="Initial public offerings scheduled in the coming weeks",
                inline=False
            )

            ipos_text = self._format_ipos(ipos[:5])
            embed.add_field(
                name="IPO Schedule",
                value=ipos_text,
                inline=False
            )

        # === FOOTER ===
        embed.set_footer(
            text="Data Sources: Polymarket | Moomoo | Alpha Vantage | Updated daily at 9:00 AM UTC",
            icon_url="https://img.icons8.com/fluency/48/finance.png"
        )

        return embed

    def _get_confidence_level(self, probability: str) -> str:
        """Get confidence level category."""
        try:
            prob_str = str(probability).replace('%', '').strip()
            prob_num = float(prob_str)
            if prob_num >= 70:
                return "High"
            elif prob_num >= 50:
                return "Medium"
            else:
                return "Low"
        except:
            return "Unknown"

    def _format_polymarket_date(self, day_str: str) -> str:
        """Format Polymarket date with current month/year."""
        try:
            # Get current date
            now = dt.datetime.now()
            month = now.month
            year = now.year

            day = int(day_str)

            # Simple logic: assume dates are in current month unless clearly in the past
            # If the day is less than current day by a lot, it might be from next month
            # But typically, Polymarket shows future earnings, so we use current month
            return f"{year}-{month:02d}-{day:02d}"
        except:
            return day_str

    def _format_polymarket_section(self, earnings_data: list) -> str:
        """Format Polymarket earnings data section."""
        lines = []
        for e in earnings_data:
            ticker = e.get('ticker', 'N/A')
            eps = e.get('eps_forecast', 'N/A')
            prob = e.get('probability', 'N/A')
            time = e.get('time', 'N/A')
            date = self._format_polymarket_date(e.get('date', ''))

            lines.append(f"{ticker} | EPS: {eps} | {prob} | {time} | {date}")

        return "\n".join(lines) if lines else "No data available"

    def _format_sectors_table(self, sectors_data: list) -> str:
        """Format sectors data as a clean table."""
        lines = []
        lines.append("```")
        lines.append(f"{'Sector':<20} {'Change':<10} {'Leader':<15} {'Up/Down':<8}")
        lines.append("-" * 60)

        for s in sectors_data:
            name = (s.get('plateName', 'N/A') or 'N/A')[:19]
            change = s.get('changeRatio', 'N/A')
            if change is None:
                change = 'N/A'
            else:
                # Format as percentage with 2 decimal places
                try:
                    change = f"{float(change):.2f}%"
                except (ValueError, TypeError):
                    change = str(change)
            leader = (s.get('stockName', 'N/A') or 'N/A')[:14]
            up = s.get('priceRiseCount', 0)
            down = s.get('priceFallCount', 0)
            if up is None:
                up = 0
            if down is None:
                down = 0

            lines.append(f"{name:<20} {change:<10} {leader:<15} {up}/{down:<8}")

        lines.append("```")
        return "\n".join(lines)

    def _format_earnings(self, earnings_data: list) -> str:
        """Format earnings data."""
        lines = []
        for e in earnings_data:
            symbol = e.get('symbol', 'N/A')
            name = e.get('name', 'N/A')
            date = e.get('reportDate', 'N/A')
            eps = e.get('estimateEPS', 'N/A')

            lines.append(f"{symbol} | {name} | {date} | EPS: {eps}")

        return "\n".join(lines) if lines else "No upcoming earnings"

    def _format_ipos(self, ipos_data: list) -> str:
        """Format IPO data."""
        lines = []
        for i in ipos_data:
            symbol = i.get('symbol', 'N/A')
            name = i.get('name', 'N/A')
            date = i.get('ipoDate', 'N/A')
            range_val = i.get('priceRange', 'TBD')

            lines.append(f"{symbol} | {name} | {date} | Range: {range_val}")

        return "\n".join(lines) if lines else "No upcoming IPOs"
