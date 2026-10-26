from bot.models import ACCEPTED, DONE, IN_PROGRESS, NEW

TEXTS: dict[str, dict[str, str]] = {
    "uz": {
        "choose_lang": "Tilni tanlang\nВыберите язык",
        "menu": "Bo'limni tanlang",
        "btn_appeal": "Murojaatlar",
        "btn_check": "Murojaatni tekshirish",
        "btn_lang": "Tilni o'zgartirish",
        "btn_back": "⬅️ Orqaga",
        "btn_cancel": "✖️ Bekor qilish",
        "btn_send": "Murojaatni jo'natish",
        "btn_share_phone": "📱 Raqamni yuborish",
        "btn_edit_profile": "✏️ Ism/telefonni o'zgartirish",
        "ask_name": "Ism-familiyangizni kiriting",
        "bad_name": "Ism-familiya 2 dan 100 gacha belgidan iborat bo'lishi kerak. Qayta kiriting",
        "ask_phone": "Telefon raqamingizni kiriting",
        "bad_phone": "Telefon raqami noto'g'ri. Masalan: +998901234567. Qayta kiriting",
        "own_contact": "Iltimos, o'zingizning raqamingizni yuboring",
        "ask_district": "Hodisa sodir bo'lgan tumanni tanlang",
        "ask_department": "Murojaat yo'nalishini tanlang",
        "ask_subject": "Murojaat mavzusini kiriting",
        "bad_subject": "Mavzu 3 dan {max} gacha belgidan iborat bo'lishi kerak. Qayta kiriting",
        "ask_body": "Murojaat mazmunini kiriting",
        "bad_body": "Mazmun 10 dan {max} gacha belgidan iborat bo'lishi kerak. Qayta kiriting",
        "ask_files": "{n} tagacha fayl biriktiring yoki murojaatni jo'nating",
        "file_added": "Fayl qabul qilindi ({count}/{n}). Yana biriktiring yoki murojaatni jo'nating",
        "file_limit": "Fayllar soni {n} tadan oshmasligi kerak. Murojaatni jo'nating",
        "bad_file": "Faqat rasm, video yoki hujjat yuboring",
        "send_text": "Iltimos, matn yuboring",
        "sent": "✅ Murojaatingiz qabul qilindi.\nMurojaat raqami: <b>{id}</b>\nHolatini «Murojaatni tekshirish» bo'limida bilib olishingiz mumkin.",
        "ask_number": "Murojaat raqamini jo'nating",
        "bad_number": "Raqam noto'g'ri. Faqat raqam kiriting",
        "not_found": "Bunday raqamli murojaat topilmadi",
        "appeal_info": (
            "<b>Murojaat №{id}</b>\nHolat: {status}\nYo'nalish: {department}\n"
            "Tuman: {district}\nMavzu: {subject}\nSana: {date}"
        ),
        "status_changed": "Murojaatingiz №{id} holati o'zgardi: {status}",
        "cancelled": "Bekor qilindi",
        "unknown": "Iltimos, /start buyrug'ini yuboring",
        "st_new": "🆕 Yangi",
        "st_accepted": "✅ Qabul qilindi",
        "st_in_progress": "⏳ Ko'rib chiqilmoqda",
        "st_done": "🏁 Yakunlandi",
    },
    "ru": {
        "choose_lang": "Tilni tanlang\nВыберите язык",
        "menu": "Выберите раздел",
        "btn_appeal": "Обращения",
        "btn_check": "Проверить обращение",
        "btn_lang": "Сменить язык",
        "btn_back": "⬅️ Назад",
        "btn_cancel": "✖️ Отмена",
        "btn_send": "Отправить обращение",
        "btn_share_phone": "📱 Отправить номер",
        "btn_edit_profile": "✏️ Изменить имя/телефон",
        "ask_name": "Введите ваше имя и фамилию",
        "bad_name": "Имя и фамилия должны содержать от 2 до 100 символов. Введите заново",
        "ask_phone": "Введите ваш номер телефона",
        "bad_phone": "Неверный номер телефона. Например: +998901234567. Введите заново",
        "own_contact": "Пожалуйста, отправьте свой номер",
        "ask_district": "Выберите район, где произошло событие",
        "ask_department": "Выберите направление обращения",
        "ask_subject": "Введите тему обращения",
        "bad_subject": "Тема должна содержать от 3 до {max} символов. Введите заново",
        "ask_body": "Введите содержание обращения",
        "bad_body": "Содержание должно быть от 10 до {max} символов. Введите заново",
        "ask_files": "Прикрепите до {n} файлов или отправьте обращение",
        "file_added": "Файл принят ({count}/{n}). Прикрепите ещё или отправьте обращение",
        "file_limit": "Не более {n} файлов. Отправьте обращение",
        "bad_file": "Отправьте только фото, видео или документ",
        "send_text": "Пожалуйста, отправьте текст",
        "sent": "✅ Ваше обращение принято.\nНомер обращения: <b>{id}</b>\nСтатус можно узнать в разделе «Проверить обращение».",
        "ask_number": "Отправьте номер обращения",
        "bad_number": "Неверный номер. Введите только цифры",
        "not_found": "Обращение с таким номером не найдено",
        "appeal_info": (
            "<b>Обращение №{id}</b>\nСтатус: {status}\nНаправление: {department}\n"
            "Район: {district}\nТема: {subject}\nДата: {date}"
        ),
        "status_changed": "Статус вашего обращения №{id} изменился: {status}",
        "cancelled": "Отменено",
        "unknown": "Пожалуйста, отправьте команду /start",
        "st_new": "🆕 Новое",
        "st_accepted": "✅ Принято",
        "st_in_progress": "⏳ На рассмотрении",
        "st_done": "🏁 Завершено",
    },
}

STATUS_KEYS = {NEW: "st_new", ACCEPTED: "st_accepted", IN_PROGRESS: "st_in_progress", DONE: "st_done"}


def t(lang: str, key: str, **kw) -> str:
    text = TEXTS.get(lang, TEXTS["uz"])[key]
    return text.format(**kw) if kw else text


def status_text(lang: str, status: str) -> str:
    return t(lang, STATUS_KEYS[status])
