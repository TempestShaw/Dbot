import asyncio
import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from utils.logger import get_logger
from utils.scheduler_utils import get_timezone


class SchedulerController:
    """Scheduler controller using APScheduler to push daily updates."""

    def __init__(self, bot, config):
        self.bot = bot
        self.config = config
        self.logger = get_logger(__name__)
        self.scheduler = AsyncIOScheduler(event_loop=asyncio.get_event_loop(), timezone=get_timezone(config.timezone))

    def start(self) -> None:
        """Start scheduler with default jobs."""
        self.logger.info("Starting scheduler...")
        self.scheduler.add_job(lambda: asyncio.create_task(self.daily_update()), "cron", hour=9, minute=0)

        self.scheduler.start()
        # trigger once immediately in background
        asyncio.create_task(self.daily_update())


    async def _send_to_channel(self, text: str = None, embed: discord.Embed = None) -> None:
        """Send text or embed to the configured channel asynchronously."""
        channel_id = self.config.channel_id
        if not channel_id:
            self.logger.warning("DISCORD_CHANNEL_ID not configured; skipping scheduled send.")
            return

        channel = self.bot.get_channel(channel_id)
        if not channel:
            self.logger.warning(f"Channel {channel_id} not found; ensure bot has access.")
            return

        if embed:
            await channel.send(embed=embed)
        elif text:
            await channel.send(text)
        else:
            self.logger.warning("No message to send.")

    async def daily_update(self) -> None:
        """Job: Generate and send daily market summary (async)."""
        json_data = await self.bot.message_service.generate_daily_summary_json_async()

        embed = self._build_daily_summary_embed(json_data)

        # Send to channel directly with await
        await self._send_to_channel(embed=embed)

    def _build_daily_summary_embed(self, data: dict) -> discord.Embed:
        """Convert JSON data into a Discord Embed (with sector table)."""
        embed = discord.Embed(
            title="📊 Daily Market Summary",
            description=f"Market summary for {data.get('dates', ['N/A'])[-1]}",
            color=discord.Color.blue()
        )

        # --- Earnings section ---
        earnings = data.get("earnings", [])
        if earnings:
            top_earnings = earnings[:5]
            earnings_text = "\n".join(
                [f"**{e['symbol']}** – {e['name']} ({e['reportDate']})"
                 for e in top_earnings]
            )
            embed.add_field(name="🧾 Upcoming Earnings", value=earnings_text, inline=False)

        # --- IPO section ---
        ipos = data.get("ipos", [])
        if ipos:
            ipo_text = "\n".join(
                [f"**{i['symbol']}** – {i['name']} ({i['ipoDate']})"
                 for i in ipos]
            )
            embed.add_field(name="🚀 Upcoming IPOs", value=ipo_text, inline=False)

        # --- Top Sector section ---
        sectors = data.get("top_sectors_details", [])
        if sectors:
            table = "```text\n"
            table += f"{'Sector':<10}{'Change':<8}{'Leader':<22}{'Leader %':<8}\n"
            table += "-" * 50 + "\n"
            for s in sectors[:8]:  # Limit to 8 rows to avoid overly long embed
                name = (s['name'][:9] + '…') if len(s['name']) > 9 else s['name']
                leader = (s['leader_stock'][:20] + '…') if len(s['leader_stock']) > 20 else s['leader_stock']
                table += f"{name:<10}{s['change_pct']:<8}{leader:<22}{s['leader_change_pct']:<8}\n"
            table += "```"
            embed.add_field(name="🏭 Top Sectors", value=table, inline=False)

        embed.set_footer(text="Data source: your API provider")
        return embed
