import logging

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.types import CallbackQuery

from bot.config import get_settings
from bot.models import DONE, IN_PROGRESS
from bot.services import appeals as repo
from bot.services.delivery import refresh_post
from bot.texts import status_text, t

log = logging.getLogger(__name__)

router = Router()
# only presses made inside the staff group are handled
router.callback_query.filter(F.message.chat.id == get_settings().group_id)

_NEW_STATUS = {"prg": IN_PROGRESS, "done": DONE}


def _staff_name(cb: CallbackQuery) -> str:
    user = cb.from_user
    return user.full_name + (f" (@{user.username})" if user.username else "")


@router.callback_query(F.data.regexp(r"^ap:(acc|prg|done):\d+$"))
async def on_action(cb: CallbackQuery, bot: Bot) -> None:
    _, action, raw_id = cb.data.split(":")
    appeal_id = int(raw_id)

    if action == "acc":
        ok = await repo.accept(appeal_id, cb.from_user.id, _staff_name(cb))
        denied = "Bu murojaatni boshqa xodim qabul qilgan"
    else:
        ok = await repo.change_status(appeal_id, cb.from_user.id, _NEW_STATUS[action])
        denied = "Holatni faqat mas'ul xodim o'zgartira oladi"

    appeal = await repo.get_appeal(appeal_id)
    if appeal is None:
        await cb.answer("Murojaat topilmadi", show_alert=True)
        return

    try:
        await refresh_post(bot, appeal)  # also repairs stale buttons after a rejected press
    except TelegramAPIError:
        log.exception("Could not refresh post of appeal %s", appeal_id)

    if not ok:
        await cb.answer(denied, show_alert=True)
        return

    await cb.answer("✅")
    lang = await repo.get_lang(appeal.user_id)
    try:
        await bot.send_message(
            appeal.user_id,
            t(lang, "status_changed", id=appeal.id, status=status_text(lang, appeal.status)),
        )
    except TelegramAPIError:
        log.warning("User %s could not be notified about appeal %s", appeal.user_id, appeal.id)
