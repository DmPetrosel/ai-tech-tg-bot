from app.database.models import async_session, User
from sqlalchemy import select

async def get_user(tg_id: int) -> User:
    async with async_session() as session:
        return await session.scalar(select(User).where(User.tg_id == tg_id))

async def create_or_update_user(tg_id: int, full_name: str, gender: str, age: str, ai_interest: str):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            user.gender = gender
            user.age = age
            user.ai_interest = ai_interest
            user.is_registered = True
        else:
            session.add(User(
                tg_id=tg_id,
                full_name=full_name,
                gender=gender,
                age=age,
                ai_interest=ai_interest,
                is_registered=True
            ))
        await session.commit()