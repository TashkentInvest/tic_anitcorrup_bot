from sqlalchemy import select, update

from bot.db import Session
from bot.models import ACCEPTED, DONE, IN_PROGRESS, NEW, Appeal, Attachment, Department, User

# status -> statuses it may be moved from
_FROM = {ACCEPTED: (NEW,), IN_PROGRESS: (ACCEPTED,), DONE: (ACCEPTED, IN_PROGRESS)}


async def get_lang(user_id: int) -> str:
    async with Session() as s:
        user = await s.get(User, user_id)
        return user.lang if user else "uz"


async def set_lang(user_id: int, lang: str) -> None:
    async with Session() as s, s.begin():
        user = await s.get(User, user_id)
        if user:
            user.lang = lang
        else:
            s.add(User(id=user_id, lang=lang))


async def get_profile(user_id: int) -> tuple[str | None, str | None]:
    async with Session() as s:
        user = await s.get(User, user_id)
        if user and user.full_name and user.phone:
            return user.full_name, user.phone
        # profile predates this feature: reuse the data from the user's latest appeal
        last = await s.scalar(
            select(Appeal).where(Appeal.user_id == user_id).order_by(Appeal.id.desc()).limit(1)
        )
        return (last.full_name, last.phone) if last else (None, None)


async def save_profile(user_id: int, full_name: str, phone: str) -> None:
    async with Session() as s, s.begin():
        user = await s.get(User, user_id)
        user.full_name, user.phone = full_name, phone


async def user_exists(user_id: int) -> bool:
    async with Session() as s:
        return await s.get(User, user_id) is not None


async def list_departments() -> list[Department]:
    async with Session() as s:
        return list((await s.scalars(select(Department).order_by(Department.id))).all())


async def get_department(department_id: int) -> Department:
    async with Session() as s:
        return await s.get_one(Department, department_id)


async def create_appeal(user_id: int, data: dict, files: list[dict]) -> int:
    async with Session() as s, s.begin():
        appeal = Appeal(
            user_id=user_id,
            full_name=data["full_name"],
            phone=data["phone"],
            district=data["district"],
            department_id=data["department_id"],
            subject=data["subject"],
            body=data["body"],
            attachments=[Attachment(file_id=f["file_id"], kind=f["kind"]) for f in files],
        )
        s.add(appeal)
        await s.flush()
        return appeal.id


async def get_appeal(appeal_id: int, user_id: int | None = None) -> Appeal | None:
    async with Session() as s:
        appeal = await s.get(Appeal, appeal_id)
        if appeal and user_id is not None and appeal.user_id != user_id:
            return None
        return appeal


async def undelivered_ids(limit: int = 20) -> list[int]:
    async with Session() as s:
        rows = await s.scalars(
            select(Appeal.id)
            .where(Appeal.group_message_id.is_(None))
            .order_by(Appeal.id)
            .limit(limit)
        )
        return list(rows.all())


async def mark_delivered(appeal_id: int, message_id: int) -> None:
    async with Session() as s, s.begin():
        await s.execute(update(Appeal).where(Appeal.id == appeal_id).values(group_message_id=message_id))


async def set_topic(department_id: int, topic_id: int) -> None:
    async with Session() as s, s.begin():
        await s.execute(update(Department).where(Department.id == department_id).values(topic_id=topic_id))


async def accept(appeal_id: int, user_id: int, name: str) -> bool:
    """Atomic claim: only the first staff member to press wins."""
    async with Session() as s, s.begin():
        res = await s.execute(
            update(Appeal)
            .where(Appeal.id == appeal_id, Appeal.status == NEW, Appeal.assignee_id.is_(None))
            .values(status=ACCEPTED, assignee_id=user_id, assignee_name=name)
        )
        return res.rowcount == 1


async def change_status(appeal_id: int, user_id: int, new_status: str) -> bool:
    """Only the assignee may move the appeal forward."""
    async with Session() as s, s.begin():
        res = await s.execute(
            update(Appeal)
            .where(
                Appeal.id == appeal_id,
                Appeal.assignee_id == user_id,
                Appeal.status.in_(_FROM[new_status]),
            )
            .values(status=new_status)
        )
        return res.rowcount == 1
