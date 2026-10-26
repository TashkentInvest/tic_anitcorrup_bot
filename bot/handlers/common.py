from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards import lang_kb, menu_kb
from bot.services import appeals as repo
from bot.texts import t

router = Router()
router.message.filter(F.chat.type == "private")
router.callback_query.filter(F.message.chat.type == "private")


async def clear_markup(cb: CallbackQuery) -> None:
    try:
        await cb.message.edit_reply_markup(reply_markup=None)
    except TelegramBadRequest:
        pass


@router.message(CommandStart())
async def start(message: Message, state: FSMContext) -> None:
    await state.clear()
    uid = message.from_user.id
    if await repo.user_exists(uid):
        lang = await repo.get_lang(uid)
        await message.answer(t(lang, "menu"), reply_markup=menu_kb(lang))
    else:
        await message.answer(t("uz", "choose_lang"), reply_markup=lang_kb())


@router.callback_query(F.data.in_({"lang:uz", "lang:ru"}))
async def choose_lang(cb: CallbackQuery, state: FSMContext) -> None:
    lang = cb.data.split(":")[1]
    await state.clear()
    await repo.set_lang(cb.from_user.id, lang)
    await clear_markup(cb)
    await cb.message.answer(t(lang, "menu"), reply_markup=menu_kb(lang))
    await cb.answer()


@router.callback_query(F.data == "menu:lang")
async def change_lang(cb: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await clear_markup(cb)
    await cb.message.answer(t("uz", "choose_lang"), reply_markup=lang_kb())
    await cb.answer()


@router.callback_query(F.data == "flow:cancel")
async def cancel(cb: CallbackQuery, state: FSMContext) -> None:
    lang = await repo.get_lang(cb.from_user.id)
    await state.clear()
    await clear_markup(cb)
    await cb.message.answer(t(lang, "menu"), reply_markup=menu_kb(lang))
    await cb.answer()
