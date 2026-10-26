import re
from html import escape

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.data import DISTRICT_BY_CODE
from bot.handlers.common import clear_markup
from bot.keyboards import back_kb
from bot.services import appeals as repo
from bot.services.delivery import fmt_date
from bot.states import CheckForm
from bot.texts import status_text, t

router = Router()
router.message.filter(F.chat.type == "private")
router.callback_query.filter(F.message.chat.type == "private")


@router.callback_query(F.data == "menu:check")
async def begin(cb: CallbackQuery, state: FSMContext) -> None:
    lang = await repo.get_lang(cb.from_user.id)
    await state.clear()
    await state.set_state(CheckForm.number)
    await state.update_data(lang=lang)
    await clear_markup(cb)
    await cb.message.answer(t(lang, "ask_number"), reply_markup=back_kb(lang))
    await cb.answer()


@router.message(CheckForm.number, F.text)
async def got_number(message: Message, state: FSMContext) -> None:
    lang = (await state.get_data())["lang"]
    found = re.search(r"\d+", message.text)
    if not found or len(found.group()) > 9:
        await message.answer(t(lang, "bad_number"), reply_markup=back_kb(lang))
        return
    # a user can only look up their own appeals
    appeal = await repo.get_appeal(int(found.group()), user_id=message.from_user.id)
    if appeal is None:
        await message.answer(t(lang, "not_found"), reply_markup=back_kb(lang))
        return
    uz, ru = DISTRICT_BY_CODE.get(appeal.district, (appeal.district, appeal.district))
    dep = appeal.department
    await message.answer(
        t(
            lang,
            "appeal_info",
            id=appeal.id,
            status=status_text(lang, appeal.status),
            department=dep.name_uz if lang == "uz" else dep.name_ru,
            district=uz if lang == "uz" else ru,
            subject=escape(appeal.subject),
            date=fmt_date(appeal),
        ),
        reply_markup=back_kb(lang),
    )


@router.message(CheckForm.number)
async def not_text(message: Message, state: FSMContext) -> None:
    lang = (await state.get_data())["lang"]
    await message.answer(t(lang, "bad_number"), reply_markup=back_kb(lang))

