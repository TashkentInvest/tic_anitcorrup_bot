import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage, SimpleEventIsolation

from bot.config import get_settings
from bot.db import engine, init_db
from bot.handlers import appeal, check, common, staff
from bot.services.delivery import ensure_topics, retry_loop

log = logging.getLogger("bot")


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    settings = get_settings()

    await init_db()
    bot = Bot(settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    # per-user event isolation: several photos sent at once are processed one by one
    dp = Dispatcher(storage=MemoryStorage(), events_isolation=SimpleEventIsolation())
    dp.include_routers(common.router, appeal.router, check.router, staff.router)

    try:
        await ensure_topics(bot)
    except Exception:
        log.exception("Topic setup failed (is the bot an admin with 'Manage topics' in the group?)")

    retry_task = asyncio.create_task(retry_loop(bot))
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        retry_task.cancel()
        await bot.session.close()
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
