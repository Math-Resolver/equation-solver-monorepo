import asyncio
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def schedule_history_persistence(
    username: str,
    equation: str,
    result: str,
    steps: list[dict],
) -> None:
    async def _runner() -> None:
        try:
            await save_equation_history(
                username=username,
                equation=equation,
                result=result,
                steps=steps,
            )
        except Exception:
            logger.exception("Failed to persist equation history")

    asyncio.create_task(_runner())
