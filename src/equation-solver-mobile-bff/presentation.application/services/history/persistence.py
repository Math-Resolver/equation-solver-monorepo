import asyncio
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


async def save_equation_history(
    username: str,
    equation: str,
    result: str,
    steps: list[dict],
) -> None:
    # TODO: implementar a persistência em banco de dados
    await asyncio.sleep(0)
    _ = {
        "username": username,
        "equation": equation,
        "result": result,
        "steps": steps,
        "createdAt": datetime.now(timezone.utc),
    }


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
