import logging

logger = logging.getLogger(__name__)


async def save_equation_history(
    username: str,
    equation: str,
    result: str,
    steps: list[dict],
) -> None:
    logger.info(
        "History persistence is not implemented yet",
        extra={
            "username": username,
            "equation": equation,
            "result": result,
            "steps": steps,
        },
    )


async def schedule_history_persistence(
    username: str,
    equation: str,
    result: str,
    steps: list[dict],
) -> None:
    await save_equation_history(
        username=username,
        equation=equation,
        result=result,
        steps=steps,
    )
