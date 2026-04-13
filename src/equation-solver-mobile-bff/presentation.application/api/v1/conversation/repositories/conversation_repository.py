from datetime import datetime, timedelta, timezone

from fastapi import Depends

from api.v1.conversation.schemas.conversation import Conversation
from api.v1.dependencies.auth import AuthenticatedUser, get_current_user


def get_recent_conversation_dep(
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> Conversation | None:
    """
    Fetches the most recent conversation for the user within the last 12 hours.

    TODO: replace with a real database query using current_user.user_id
    and the time window: now - 12 hours.
    Return None if no conversation exists within the period.
    """
    cutoff = datetime.now(tz=timezone.utc) - timedelta(hours=12)  # noqa: F841
    user_id = current_user.user_id  # noqa: F841
    return None


def get_past_conversations_dep(
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> list[Conversation]:
    """
    Fetches all past conversations for the current user.

    TODO: replace with a real database query filtered by current_user.user_id.
    """
    user_id = current_user.user_id  # noqa: F841
    return []
