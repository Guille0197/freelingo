"""Create a short-lived first-user invitation without opening public registration.

Run inside the backend container: python -m app.create_private_invite
"""

import asyncio
import secrets

from redis.asyncio import Redis
from sqlalchemy import func, select

from app.core.config import settings
from app.core.database import AsyncSessionLocal, engine
from app.models.user import User


async def main() -> None:
    try:
        async with AsyncSessionLocal() as db:
            count = await db.scalar(select(func.count(User.id)))
        if count:
            raise SystemExit("Users already exist. Use an administrator invitation instead.")
        if settings.ALLOW_REGISTRATION or not settings.FIRST_USER_IS_ADMIN:
            raise SystemExit("Require closed registration and FIRST_USER_IS_ADMIN=true.")
        token = secrets.token_urlsafe(32)
        async with Redis.from_url(settings.REDIS_URL, decode_responses=True) as redis:
            await redis.setex(f"invite:{token}", 900, "first-user")
        print(f"{settings.APP_BASE_URL.rstrip('/')}/register?invite={token}")
        print("Single-use invitation expires in 15 minutes. Keep this link private.")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
