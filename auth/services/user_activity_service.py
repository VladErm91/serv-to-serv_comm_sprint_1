import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from models.user import UserActionHistory


async def log_user_action(session: AsyncSession, user_id, action):
    activity = UserActionHistory(
        user_id=user_id,
        action=action,
        timestamp=datetime.datetime.now(),
    )
    session.add(activity)
    await session.commit()
