import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from utils.logger import get_logger
from utils.scheduler_utils import get_timezone


class SchedulerController:
    """Scheduler controller using APScheduler to push daily updates.

    Responsibilities:
    - Schedule jobs (e.g., daily market summary)
    - Post messages to configured Discord channel via BotController
    """

    def __init__(self, bot, config):
        self.bot = bot
        self.config = config
        self.logger = get_logger(__name__)
        self.scheduler = AsyncIOScheduler(timezone=get_timezone(config.timezone))

    def start(self) -> None:
        """Start scheduler with default jobs."""
        self.logger.info("Starting scheduler...")
        # Daily summary push at 09:00 local time
        self.scheduler.add_job(self.daily_update, "cron", hour=9, minute=0)
        self.scheduler.start()
        json = self.bot.message_service.generate_daily_summary_json()
        print(json)

    async def _send_to_channel(self, text: str) -> None:
        """Send text to the configured channel asynchronously."""
        channel_id = self.config.channel_id
        if not channel_id:
            self.logger.warning("DISCORD_CHANNEL_ID not configured; skipping scheduled send.")
            return

        channel = self.bot.get_channel(channel_id)
        if not channel:
            self.logger.warning(f"Channel {channel_id} not found; ensure bot has access.")
            return

        await channel.send(text)

    def daily_update(self) -> None:
        """Job: Generate and send daily market summary."""
        text = self.bot.message_service.generate_daily_summary_text()
        # Scheduler executes in sync context; schedule coroutine for Discord send
        asyncio.create_task(self._send_to_channel(text))