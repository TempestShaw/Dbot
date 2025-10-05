import json
import discord
from services.message_service import MessageService
from utils.logger import get_logger
from typing import Optional


class BotController(discord.Client):
    """Discord bot controller handling events and commands.

    Responsibilities:
    - Initialize MessageService
    - Handle lifecycle events: on_ready
    - Handle commands: !today (text), !today_json (JSON)
    - Cooperate with SchedulerController for scheduled pushes
    """

    def __init__(self, config):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)

        self.config = config
        self.message_service = MessageService(config)
        self.logger = get_logger(__name__)
        self._scheduler: Optional[object] = None

    def attach_scheduler(self, scheduler) -> None:
        """Attach a scheduler instance to be started when bot is ready."""
        self._scheduler = scheduler

    async def on_ready(self):
        self.logger.info(f"Logged in as {self.user}")
        if self._scheduler:
            self._scheduler.start()

    async def on_message(self, message: discord.Message):
        # Ignore messages from bot itself
        if message.author == self.user:
            return

        content = message.content.strip()
        if content.startswith("!today"):
            text = await self.message_service.generate_daily_summary_text_async()
            await message.channel.send(text)

        elif content.startswith("!today_json"):
            payload = await self.message_service.generate_daily_summary_json_async()
            await message.channel.send(
                f"```json\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n```"
            )