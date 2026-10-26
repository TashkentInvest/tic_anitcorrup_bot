from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.data import DISTRICTS
from bot.models import ACCEPTED, IN_PROGRESS, NEW, Department
from bot.texts import t


def lang_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="O'zbekcha", callback_data="lang:uz")
    b.button(text="Русский", callback_data="lang:ru")
    return b.adjust(2).as_markup()


def menu_kb(lang: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=t(lang, "btn_appeal"), callback_data="menu:appeal")
    b.button(text=t(lang, "btn_check"), callback_data="menu:check")
    b.button(text=t(lang, "btn_lang"), callback_data="menu:lang")
    return b.adjust(2, 1).as_markup()


def cancel_kb(lang: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=t(lang, "btn_cancel"), callback_data="flow:cancel")
    return b.as_markup()


def back_kb(lang: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=t(lang, "btn_back"), callback_data="flow:cancel")
    return b.as_markup()


def phone_kb(lang: str) -> ReplyKeyboardMarkup:
    # Telegram only supports contact sharing through a reply keyboard.
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t(lang, "btn_share_phone"), request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def districts_kb(lang: str, editable: bool = False) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for code, uz, ru in DISTRICTS:
        b.button(text=uz if lang == "uz" else ru, callback_data=f"dist:{code}")
    b.adjust(2)
    if editable:
        b.row(InlineKeyboardButton(text=t(lang, "btn_edit_profile"), callback_data="profile:edit"))
    b.row(InlineKeyboardButton(text=t(lang, "btn_cancel"), callback_data="flow:cancel"))
    return b.as_markup()


def departments_kb(lang: str, departments: list[Department]) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for d in departments:
        b.button(text=d.name_uz if lang == "uz" else d.name_ru, callback_data=f"dep:{d.id}")
    b.adjust(2)
    b.row(InlineKeyboardButton(text=t(lang, "btn_cancel"), callback_data="flow:cancel"))
    return b.as_markup()


def send_kb(lang: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=t(lang, "btn_send"), callback_data="flow:send")
    b.button(text=t(lang, "btn_cancel"), callback_data="flow:cancel")
    return b.adjust(1).as_markup()


def staff_kb(appeal_id: int, status: str) -> InlineKeyboardMarkup | None:
    """Buttons under the group post. Uzbek only: staff-facing."""
    b = InlineKeyboardBuilder()
    if status == NEW:
        b.button(text="✅ Qabul qildim", callback_data=f"ap:acc:{appeal_id}")
    elif status == ACCEPTED:
        b.button(text="⏳ Ko'rib chiqilmoqda", callback_data=f"ap:prg:{appeal_id}")
        b.button(text="🏁 Yakunlandi", callback_data=f"ap:done:{appeal_id}")
    elif status == IN_PROGRESS:
        b.button(text="🏁 Yakunlandi", callback_data=f"ap:done:{appeal_id}")
    else:
        return None
    return b.adjust(1).as_markup()
