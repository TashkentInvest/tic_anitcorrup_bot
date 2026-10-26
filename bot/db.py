from sqlalchemy import inspect, select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from bot.config import get_settings
from bot.data import DEPARTMENTS
from bot.models import Base, Department

engine = create_async_engine(get_settings().database_url, pool_pre_ping=True)
Session = async_sessionmaker(engine, expire_on_commit=False)


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # create_all never alters existing tables: add profile columns if the DB predates them
        cols = await conn.run_sync(lambda c: {x["name"] for x in inspect(c).get_columns("users")})
        for name, ddl in (("full_name", "VARCHAR(100)"), ("phone", "VARCHAR(20)")):
            if name not in cols:
                await conn.execute(text(f"ALTER TABLE users ADD COLUMN {name} {ddl}"))

    async with Session() as s, s.begin():
        existing = {d.code: d for d in (await s.scalars(select(Department))).all()}
        for code, uz, ru in DEPARTMENTS:
            dep = existing.get(code)
            if dep:
                dep.name_uz, dep.name_ru = uz, ru
            else:
                s.add(Department(code=code, name_uz=uz, name_ru=ru))
