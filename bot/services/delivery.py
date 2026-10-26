import asyncio
import logging
from datetime import timezone
from html import escape
from zoneinfo import ZoneInfo

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest

from bot.config import get_settings
from bot.data import DISTRICT_BY_CODE
from bot.keyboards import staff_kb
from bot.models import Appeal, Department
from bot.services import appeals as repo
from bot.texts import status_text

log = logging.getLogger(__name__)
TZ = ZoneInfo("Asia/Tashkent")

_topic_lock = asyncio.Lock()
_is_forum: bool | None = None


def fmt_date(appeal: Appeal) -> str:
    created = appeal.created_at
    if created.tzinfo is None:  # SQLite returns naive UTC timestamps
        created = created.replace(tzinfo=timezone.utc)
    return created.astimezone(TZ).strftime("%d.%m.%Y %H:%M")


def render_post(appeal: Appeal) -> str:
    district = DISTRICT_BY_CODE.get(appeal.district, (appeal.district,))[0]
    lines = [
        f"📩 <b>Murojaat №{appeal.id}</b>",
        f"Holat: {status_text('uz', appeal.status)}",
        f"Yo'nalish: {escape(appeal.department.name_uz)}",
        f"Tuman: {escape(district)}",
        f"F.I.Sh.: {escape(appeal.full_name)}",
        f"Telefon: {escape(appeal.phone)}",
        f"Sana: {fmt_date(appeal)}",
        "",
        f"<b>Mavzu:</b> {escape(appeal.subject)}",
        escape(appeal.body),
    ]
    if appeal.assignee_name:
        lines += ["", f"👤 Mas'ul: {escape(appeal.assignee_name)}"]
    return "\n".join(lines)


async def refresh_post(bot: Bot, appeal: Appeal) -> None:
    if appeal.group_message_id is None:
        return
    try:
        await bot.edit_message_text(
            render_post(appeal),
            chat_id=get_settings().group_id,
            message_id=appeal.group_message_id,
            reply_markup=staff_kb(appeal.id, appeal.status),
        )
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise


async def _create_topic(bot: Bot, dep: Department) -> int:
    topic = await bot.create_forum_topic(get_settings().group_id, dep.name_uz)
    await repo.set_topic(dep.id, topic.message_thread_id)
    return topic.message_thread_id


async def ensure_topics(bot: Bot) -> None:
    """Create one forum topic per department (idempotent)."""
    global _is_forum
    chat = await bot.get_chat(get_settings().group_id)
    _is_forum = bool(chat.is_forum)
    if not _is_forum:
        log.warning("Group is not a forum: appeals will be posted without topics")
        return
    async with _topic_lock:
        for dep in await repo.list_departments():
            if dep.topic_id is None:
                await _create_topic(bot, dep)


async def _thread_for(bot: Bot, dep: Department, recreate: bool = False) -> int | None:
    if _is_forum is None:
        await ensure_topics(bot)
    if not _is_forum:
        return None
    async with _topic_lock:
        fresh = await repo.get_department(dep.id)  # another task may have created it meanwhile
        if fresh.topic_id is not None and not recreate:
            return fresh.topic_id
        return await _create_topic(bot, fresh)


async def _send_post(bot: Bot, appeal: Appeal, thread: int | None):
    return await bot.send_message(
        get_settings().group_id,
        render_post(appeal),
        message_thread_id=thread,
        reply_markup=staff_kb(appeal.id, appeal.status),
    )


async def _send_attachment(bot: Bot, appeal: Appeal, att, thread: int | None, reply_to: int) -> None:
    send = {"photo": bot.send_photo, "video": bot.send_video, "document": bot.send_document}[att.kind]
    await send(
        get_settings().group_id,
        att.file_id,
        message_thread_id=thread,
        reply_to_message_id=reply_to,
        caption=f"Murojaat №{appeal.id}",
    )


async def post_appeal(bot: Bot, appeal_id: int) -> None:
    appeal = await repo.get_appeal(appeal_id)
    if appeal is None or appeal.group_message_id is not None:
        return

    thread = await _thread_for(bot, appeal.department)
    try:
        msg = await _send_post(bot, appeal, thread)
    except TelegramBadRequest as e:
        if "thread" not in str(e).lower():
            raise
        # the topic was deleted by an admin: create a new one and retry once
        thread = await _thread_for(bot, appeal.department, recreate=True)
        msg = await _send_post(bot, appeal, thread)

    await repo.mark_delivered(appeal.id, msg.message_id)
    for att in appeal.attachments:
        try:
            await _send_attachment(bot, appeal, att, thread, msg.message_id)
        except TelegramAPIError:
            log.exception("Attachment %s of appeal %s was not delivered", att.id, appeal.id)


async def safe_post(bot: Bot, appeal_id: int) -> None:
    try:
        await post_appeal(bot, appeal_id)
    except Exception:
        log.exception("Appeal %s not delivered to group, will retry", appeal_id)


async def retry_loop(bot: Bot) -> None:
    """Re-send appeals that could not reach the group (group down, bot not admin, ...)."""
    interval = get_settings().retry_interval_sec
    while True:
        await asyncio.sleep(interval)
        try:
            for appeal_id in await repo.undelivered_ids():
                await safe_post(bot, appeal_id)
        except Exception:
            log.exception("Retry loop iteration failed")
