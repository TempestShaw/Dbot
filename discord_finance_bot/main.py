import asyncio
from config import load_config
from controllers.bot_controller import BotController
# Use clean scheduler controller with separated concerns
from controllers.clean_scheduler_controller import CleanSchedulerController
from utils.logger import get_logger


# Entry point: initialize Discord client and scheduler
logger = get_logger(__name__)


def main():
    """Main entry to start Discord Bot and scheduler."""
    config = load_config()
    bot = BotController(config)
    scheduler = CleanSchedulerController(bot, config)

    # Attach scheduler to bot and start when bot becomes ready
    bot.attach_scheduler(scheduler)

    logger.info("Starting Discord bot with clean scheduler architecture...")
    bot.run(config.discord_token)


if __name__ == "__main__":
    main()
