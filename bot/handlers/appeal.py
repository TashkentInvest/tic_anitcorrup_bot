import re
from html import escape

from aiogram import Bot, F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from bot.config import get_settings
from bot.data import DISTRICT_BY_CODE
from bot.handlers.common import clear_markup
from bot.keyboards import cancel_kb, departments_kb, districts_kb, menu_kb, phone_kb, send_kb
from bot.services import appeals as repo
from bot.services.delivery import safe_post
from bot.states import AppealForm
from bot.texts import t

router = Router()
router.message.filter(F.chat.type == "private")
router.callback_query.filter(F.message.chat.type == "private")

settings = get_settings()


def normalize_phone(raw: str) -> str | None:
    digits = re.sub(r"[\s\-()]", "", raw)
    if not re.fullmatch(r"\+?\d{9,15}", digits):
        return None
    if len(digits) == 9:
        return "+998" + digits
    return digits if digits.startswith("+") else "+" + digits


@router.callback_query(F.data == "menu:appeal")
async def begin(cb: CallbackQuery, state: FSMContext) -> None:
    lang = await repo.get_lang(cb.from_user.id)
    await state.clear()
    await state.set_state(AppealForm.name)
    await state.update_data(lang=lang, files=[])
    await clear_markup(cb)
    full_name, phone = await repo.get_profile(cb.from_user.id)
    if full_name and phone:
        # known user: do not ask for name and phone again
        await state.update_data(full_name=full_name, phone=phone)
        await state.set_state(AppealForm.district)
        await cb.message.answer(f"👤 {escape(full_name)}\n📱 {phone}")
        await cb.message.answer(t(lang, "ask_district"), reply_markup=districts_kb(lang, editable=True))
    else:
        await state.set_state(AppealForm.name)
        await cb.message.answer(t(lang, "ask_name"), reply_markup=cancel_kb(lang))
    await cb.answer()


@router.callback_query(AppealForm.district, F.data == "profile:edit")
async def edit_profile(cb: CallbackQuery, state: FSMContext) -> None:
    lang = (await state.get_data())["lang"]
    await state.set_state(AppealForm.name)
    await clear_markup(cb)
    await cb.message.answer(t(lang, "ask_name"), reply_markup=cancel_kb(lang))
    await cb.answer()


@router.message(AppealForm.name, F.text)
async def got_name(message: Message, state: FSMContext) -> None:
    lang = (await state.get_data())["lang"]
    name = message.text.strip()
    if not 2 <= len(name) <= 100:
        await message.answer(t(lang, "bad_name"), reply_markup=cancel_kb(lang))
        return
    await state.update_data(full_name=name)
    await state.set_state(AppealForm.phone)
    await message.answer(t(lang, "ask_phone"), reply_markup=phone_kb(lang))


async def _after_phone(message: Message, state: FSMContext, lang: str, phone: str) -> None:
    await state.update_data(phone=phone)
    data = await state.get_data()
    await repo.save_profile(message.from_user.id, data["full_name"], phone)
    await state.set_state(AppealForm.district)
    # removes the contact-sharing reply keyboard
    await message.answer(f"📱 {phone}", reply_markup=ReplyKeyboardRemove())
    await message.answer(t(lang, "ask_district"), reply_markup=districts_kb(lang))


@router.message(AppealForm.phone, F.contact)
async def got_contact(message: Message, state: FSMContext) -> None:
    lang = (await state.get_data())["lang"]
    if message.contact.user_id != message.from_user.id:
        await message.answer(t(lang, "own_contact"), reply_markup=phone_kb(lang))
        return
    phone = normalize_phone(message.contact.phone_number)
    if phone is None:
        await message.answer(t(lang, "bad_phone"), reply_markup=phone_kb(lang))
        return
    await _after_phone(message, state, lang, phone)


@router.message(AppealForm.phone, F.text)
async def got_phone_text(message: Message, state: FSMContext) -> None:
    lang = (await state.get_data())["lang"]
    phone = normalize_phone(message.text)
    if phone is None:
        await message.answer(t(lang, "bad_phone"), reply_markup=phone_kb(lang))
        return
    await _after_phone(message, state, lang, phone)


@router.callback_query(AppealForm.district, F.data.startswith("dist:"))
async def got_district(cb: CallbackQuery, state: FSMContext) -> None:
    code = cb.data.split(":", 1)[1]
    if code not in DISTRICT_BY_CODE:
        await cb.answer()
        return
    lang = (await state.get_data())["lang"]
    await state.update_data(district=code)
    await state.set_state(AppealForm.department)
    await clear_markup(cb)
    departments = await repo.list_departments()
    await cb.message.answer(t(lang, "ask_department"), reply_markup=departments_kb(lang, departments))
    await cb.answer()


@router.callback_query(AppealForm.department, F.data.startswith("dep:"))
async def got_department(cb: CallbackQuery, state: FSMContext) -> None:
    dep_id = int(cb.data.split(":", 1)[1])
    if dep_id not in {d.id for d in await repo.list_departments()}:
        await cb.answer()
        return
    lang = (await state.get_data())["lang"]
    await state.update_data(department_id=dep_id)
    await state.set_state(AppealForm.subject)
    await clear_markup(cb)
    await cb.message.answer(t(lang, "ask_subject"), reply_markup=cancel_kb(lang))
    await cb.answer()


@router.message(AppealForm.subject, F.text)
async def got_subject(message: Message, state: FSMContext) -> None:
    lang = (await state.get_data())["lang"]
    subject = message.text.strip()
    if not 3 <= len(subject) <= settings.max_subject_len:
        await message.answer(
            t(lang, "bad_subject", max=settings.max_subject_len), reply_markup=cancel_kb(lang)
        )
        return
    await state.update_data(subject=subject)
    await state.set_state(AppealForm.body)
    await message.answer(t(lang, "ask_body"), reply_markup=cancel_kb(lang))


@router.message(AppealForm.body, F.text)
async def got_body(message: Message, state: FSMContext) -> None:
    lang = (await state.get_data())["lang"]
    body = message.text.strip()
    if not 10 <= len(body) <= settings.max_body_len:
        await message.answer(t(lang, "bad_body", max=settings.max_body_len), reply_markup=cancel_kb(lang))
        return
    await state.update_data(body=body)
    await state.set_state(AppealForm.files)
    await message.answer(t(lang, "ask_files", n=settings.max_files), reply_markup=send_kb(lang))


def _extract_file(message: Message) -> dict | None:
    if message.photo:
        return {"file_id": message.photo[-1].file_id, "kind": "photo"}
    if message.video:
        return {"file_id": message.video.file_id, "kind": "video"}
    if message.document:
        return {"file_id": message.document.file_id, "kind": "document"}
    return None


@router.message(AppealForm.files, F.photo | F.video | F.document)
async def got_file(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang, files = data["lang"], data["files"]
    if len(files) >= settings.max_files:
        await message.answer(t(lang, "file_limit", n=settings.max_files), reply_markup=send_kb(lang))
        return
    files.append(_extract_file(message))
    await state.update_data(files=files)
    await message.answer(
        t(lang, "file_added", count=len(files), n=settings.max_files), reply_markup=send_kb(lang)
    )


@router.callback_query(AppealForm.files, F.data == "flow:send")
async def send_appeal(cb: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    data = await state.get_data()
    await state.clear()  # clear first: a double tap must not create a second appeal
    lang = data["lang"]
    appeal_id = await repo.create_appeal(cb.from_user.id, data, data.get("files", []))
    await clear_markup(cb)
    await cb.message.answer(t(lang, "sent", id=appeal_id))
    await cb.message.answer(t(lang, "menu"), reply_markup=menu_kb(lang))
    await cb.answer()
    await safe_post(bot, appeal_id)


@router.message(StateFilter(AppealForm))
async def fallback(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "uz")
    current = await state.get_state()
    if current == AppealForm.files.state:
        key = "bad_file"
    elif current == AppealForm.phone.state:
        key = "bad_phone"
    elif current in (AppealForm.district.state, AppealForm.department.state):
        key = "unknown"
    else:
        key = "send_text"
    await message.answer(t(lang, key))
