import asyncio

from app.database import AsyncSessionLocal
from app.models.user import User
from app.models.enums import UserRole
from app.security import hash_password


async def seed_users():
    async with AsyncSessionLocal() as db:
        admin = User(
            username="admin",
            hashed_password=hash_password("AdminPass123!"),
            role=UserRole.ADMIN,
        )

        technician = User(
            username="technician",
            hashed_password=hash_password("TechnicianPass123!"),
            role=UserRole.TECHNICIAN,
        )

        auditor = User(
            username="auditor",
            hashed_password=hash_password("AuditorPass123!"),
            role=UserRole.AUDITOR,
        )

        db.add_all([admin, technician, auditor])
        await db.commit()


if __name__ == "__main__":
    asyncio.run(seed_users())