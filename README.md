# Toshkent antikorrupsiya boti

Telegram bot (Python, aiogram 3, PostgreSQL). Citizens submit appeals; each appeal is posted
to a staff forum group, into the topic of the chosen department. A staff member presses
**Qabul qildim** to claim it; only that person can then move it to *Ko'rib chiqilmoqda* /
*Yakunlandi*. The citizen is notified of every status change and can look the appeal up by number.

## Setup
1. Create the database: `CREATE DATABASE anticorrup;`
2. Copy `.env.example` to `.env` and fill in `BOT_TOKEN`, `GROUP_ID`, `DATABASE_URL`.
3. Staff group: a supergroup with **Topics enabled**; add the bot as admin with the
   **Manage topics** right. Get its id (starts with `-100`) e.g. by forwarding a group message to @RawDataBot.
4. Install and run:
   ```
   python -m venv .venv
   .venv\Scripts\pip install -r requirements.txt
   .venv\Scripts\python -m bot.main
   ```
Tables are created on first start; departments and their topics are created automatically.

## Customising
- Departments: `bot/data.py` (`DEPARTMENTS`), applied on next start. New departments get a new topic.
- Districts: `bot/data.py` (`DISTRICTS`).
- All user texts (uz/ru): `bot/texts.py`.

## Behaviour notes
- If the group is unreachable, the appeal is still saved and re-sent every 60 s until delivered.
- If the group is not a forum, appeals are posted to the main chat without topics.
- Conversation state is kept in memory: a restart interrupts forms in progress (saved appeals are safe).
