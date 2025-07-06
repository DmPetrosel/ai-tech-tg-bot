from sqlalchemy import BigInteger, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

engine = create_async_engine(url="sqlite+aiosqlite:///db.sqlite3")
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=True)  # Новое поле
    phone_number: Mapped[str] = mapped_column(String(30), nullable=True)
    gender: Mapped[str] = mapped_column(String(10))
    age: Mapped[str] = mapped_column(String(10))
    ai_interest: Mapped[str] = mapped_column(String(20))
    is_registered: Mapped[bool] = mapped_column(default=False)


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
