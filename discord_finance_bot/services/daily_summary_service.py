"""
Daily Summary Service - Handles daily summary generation logic.

This service is responsible for:
1. Generating daily market summary data
2. Formatting the data into Discord embeds
3. Sending messages to Discord channels

The scheduler simply calls this service without knowing the implementation details.
"""

import asyncio
import discord
from typing import Optional
from utils.logger import get_logger


class DailySummaryService:
    """Service for generating and sending daily market summaries."""

    def __init__(self, bot, config):
        self.bot = bot
        self.config = config
        self.logger = get_logger(__name__)

    async def send_daily_summary(self) -> None:
        """Generate and send daily market summary to Discord."""
        try:
            self.logger.info("Generating daily market summary...")

            # Generate summary data
            summary_data = await self._generate_summary_data()

            # Build Discord embed
            embed = self._build_professional_embed(summary_data)

            # Send to Discord
            await self._send_embed_to_channel(embed)

            self.logger.info("Daily market summary sent successfully")

        except Exception as e:
            self.logger.error(f"Failed to send daily summary: {e}")
            raise

    async def _generate_summary_data(self) -> dict:
        """Generate summary data from all sources."""
        return await self.bot.message_service.generate_daily_summary_json_async()

    async def _send_embed_to_channel(self, embed: discord.Embed) -> None:
        """Send embed to the configured Discord channel."""
        channel_id = self.config.channel_id

        if not channel_id:
            self.logger.warning("DISCORD_CHANNEL_ID not configured; skipping daily summary send.")
            return

        channel = self.bot.get_channel(channel_id)

        if not channel:
            self.logger.warning(f"Channel {channel_id} not found; ensure bot has access.")
            return

        try:
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
        ipos = data.get("ipos", [])

        # Create main embed
        embed = discord.Embed(
            title="Daily Market Summary",
            description=f"Comprehensive market analysis for {data.get('dates', ['N/A'])[-1]}",
            color=0x3498db,  # Professional blue
            url="https://polymarket.com/earnings"
        )

        # Set professional branding
        embed.set_author(
            name="Market Intelligence System",
            url="https://github.com/your-repo",
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

        # === SECTION 3: IPO CALENDAR ===
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
            text="Data Sources: Polymarket | Moomoo | Updated daily at 9:00 AM UTC",
            icon_url="https://img.icons8.com/fluency/48/finance.png"
        )

        return embed

    def _get_confidence_level(self, probability: str) -> str:
        """Get confidence level category."""
        try:
            prob_num = int(probability.replace('%', ''))
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
        import datetime as dt
        try:
            # Get current date
            now = dt.datetime.now()
            month = now.month
            year = now.year

            day = int(day_str)
            # Check if the date is in the past month (new month started)
            if day > now.day:
                # Might be from previous month
                if now.month == 1:
                    month = 12
                    year = year - 1
                else:
                    month = month - 1

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

            lines.append(f"{ticker} | {eps} | {prob} | {time} | {date}")

        return "\n".join(lines) if lines else "No data available"

    def _format_sectors_table(self, sectors_data: list) -> str:
        """Format sectors data as a clean table."""
        lines = []
        lines.append("```")
        lines.append(f"{'Sector':<20} {'Change':<10} {'Leader':<20} {'Up/Down':<8}")
        lines.append("-" * 65)

        for s in sectors_data:
            name = (s.get('plateName', 'N/A') or 'N/A')[:19]
            change = s.get('changeRatio', 'N/A')
            leader = (s.get('stockName', 'N/A') or 'N/A')[:19]
            up = s.get('priceRiseCount', 0)
            down = s.get('priceFallCount', 0)

            lines.append(f"{name:<20} {change:<10} {leader:<20} {up}/{down:<8}")

        lines.append("```")
        return "\n".join(lines)

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
