"""
Scheduler Controller - Only handles scheduling logic.

This controller is responsible for:
1. Managing the APScheduler
2. Scheduling jobs
3. Triggering the DailySummaryService

It does NOT contain any daily summary generation logic.
That is delegated to the DailySummaryService.
"""

import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from utils.logger import get_logger
from utils.scheduler_utils import get_timezone
from services.daily_summary_service import DailySummaryService


class SchedulerController:
    """Scheduler controller that only handles scheduling."""

    def __init__(self, bot, config):
        self.bot = bot
        self.config = config
        self.logger = get_logger(__name__)
        self.scheduler = AsyncIOScheduler(
            event_loop=asyncio.get_event_loop(),
            timezone=get_timezone(config.timezone)
        )
        # Create the daily summary service
        self.daily_summary_service = DailySummaryService(bot, config)

    def start(self) -> None:
        """Start the scheduler with configured jobs."""
        self.logger.info("Starting scheduler...")

        # Schedule the daily summary job
        self.scheduler.add_job(
            self._execute_daily_summary_job,
            "cron",
            hour=9,
            minute=0,
            id="daily_summary_job",
            name="Daily Market Summary",
            replace_existing=True
        )

        self.logger.info("Scheduler started successfully")
        self.scheduler.start()

        # Trigger once immediately for testing
        self.logger.info("Triggering initial daily summary...")
        asyncio.create_task(self._execute_daily_summary_job())

    async def _execute_daily_summary_job(self) -> None:
        """
        Execute the daily summary job.

        This is a simple wrapper that delegates to the DailySummaryService.
        The scheduler doesn't need to know HOW the summary is generated,
        only THAT it should be generated.
        """
        self.logger.info("Executing daily summary job...")

        try:
            # Delegate the entire daily summary process to the service
            # This keeps the scheduler clean and focused on timing
            await self.daily_summary_service.send_daily_summary()
            self.logger.info("Daily summary job delegated to DailySummaryService")

        except Exception as e:
            self.logger.error(f"Failed to execute daily summary job: {e}")
            raise

    def shutdown(self) -> None:
        """Shutdown the scheduler gracefully."""
        self.logger.info("Shutting down scheduler...")
        self.scheduler.shutdown()
        self.logger.info("Scheduler shutdown complete")

    def add_custom_job(self, func, trigger: str, **kwargs) -> str:
        """
        Add a custom job to the scheduler.

        Args:
            func: The function to execute
            trigger: The trigger type ('cron', 'interval', 'date')
            **kwargs: Additional arguments for the trigger

        Returns:
            The job ID
        """
        job_id = f"custom_job_{len(self.scheduler.get_jobs())}"
        self.scheduler.add_job(func, trigger, id=job_id, **kwargs)
        self.logger.info(f"Added custom job: {job_id}")
        return job_id

    def remove_job(self, job_id: str) -> None:
        """Remove a job from the scheduler."""
        try:
            self.scheduler.remove_job(job_id)
            self.logger.info(f"Removed job: {job_id}")
        except Exception as e:
            self.logger.error(f"Failed to remove job {job_id}: {e}")

    def get_scheduled_jobs(self) -> list:
        """Get all scheduled jobs."""
        jobs = self.scheduler.get_jobs()
        return [
            {
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            }
            for job in jobs
        ]

    def pause_job(self, job_id: str) -> None:
        """Pause a scheduled job."""
        try:
            self.scheduler.pause_job(job_id)
            self.logger.info(f"Paused job: {job_id}")
        except Exception as e:
            self.logger.error(f"Failed to pause job {job_id}: {e}")

    def resume_job(self, job_id: str) -> None:
        """Resume a paused job."""
        try:
            self.scheduler.resume_job(job_id)
            self.logger.info(f"Resumed job: {job_id}")
        except Exception as e:
            self.logger.error(f"Failed to resume job {job_id}: {e}")
