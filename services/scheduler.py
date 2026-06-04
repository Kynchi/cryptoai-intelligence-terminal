from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone

from services.data_ingestion import DataIngestionService
from training.train import TrainingPipeline
from utils.config import Settings, load_settings


LOGGER = logging.getLogger(__name__)


@dataclass
class SchedulerStatus:
    started_at: str
    data_updates: int
    retraining_jobs: int
    messages: list[str]


class RetrainingScheduler:
    """Small in-process scheduler hook for API deployments.

    Production deployments can run the same methods from cron, GitHub Actions, or a
    container scheduler; keeping it here lets `/realtime` trigger the exact same code path.
    """

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or load_settings()
        self.ingestion = DataIngestionService(self.settings)
        self.training = TrainingPipeline(self.settings)

    def run_once(self, retrain: bool = False, model_name: str | None = None) -> SchedulerStatus:
        messages: list[str] = []
        started_at = datetime.now(timezone.utc).isoformat()
        updates = self.ingestion.update_all()
        messages.extend(result.message for result in updates)

        retraining_jobs = 0
        if retrain:
            for symbol in self.settings.coins:
                self.training.train(symbol=symbol, model_name=model_name)
                retraining_jobs += 1

        LOGGER.info("Scheduler run completed: %s data updates, %s trainings", len(updates), retraining_jobs)
        return SchedulerStatus(
            started_at=started_at,
            data_updates=len(updates),
            retraining_jobs=retraining_jobs,
            messages=messages,
        )
