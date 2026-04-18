import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler

logger = logging.getLogger(__name__)

class OrchestratorScheduler:
    def __init__(self, orchestrator):
        self.orch = orchestrator
        self.scheduler = AsyncIOScheduler()
        self._job = None

    def start_autonomous_mode(self, interval_seconds: int = 60):
        """Starts the background scheduler to process workflows automatically."""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("🕒 Scheduler started.")

        if self._job:
            self.scheduler.remove_job(self._job.id)

        self._job = self.scheduler.add_job(
            self.orch.autonomous_tick,
            'interval',
            seconds=interval_seconds,
            id='autonomous_tick'
        )
        logger.info(f"🤖 Autonomous mode activated! Ticking every {interval_seconds} seconds.")

    def stop_autonomous_mode(self):
        """Stops the autonomous workflow execution."""
        if self._job:
            self.scheduler.remove_job(self._job.id)
            self._job = None
            logger.info("🛑 Autonomous mode stopped.")
