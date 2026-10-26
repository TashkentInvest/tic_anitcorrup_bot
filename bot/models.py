from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

NEW, ACCEPTED, IN_PROGRESS, DONE = "new", "accepted", "in_progress", "done"


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # telegram id
    lang: Mapped[str] = mapped_column(String(2), default="uz")
    full_name: Mapped[str | None] = mapped_column(String(100))
    phone: Mapped[str | None] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True)
    name_uz: Mapped[str] = mapped_column(String(100))
    name_ru: Mapped[str] = mapped_column(String(100))
    topic_id: Mapped[int | None] = mapped_column(BigInteger)


class Appeal(Base):
    __tablename__ = "appeals"

    id: Mapped[int] = mapped_column(primary_key=True)  # public appeal number
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), index=True)
    full_name: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(20))
    district: Mapped[str] = mapped_column(String(32))
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"))
    subject: Mapped[str] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(16), default=NEW, index=True)
    assignee_id: Mapped[int | None] = mapped_column(BigInteger)
    assignee_name: Mapped[str | None] = mapped_column(String(200))
    group_message_id: Mapped[int | None] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    department: Mapped[Department] = relationship(lazy="joined")
    attachments: Mapped[list["Attachment"]] = relationship(
        lazy="selectin", order_by="Attachment.id"
    )


class Attachment(Base):
    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(primary_key=True)
    appeal_id: Mapped[int] = mapped_column(ForeignKey("appeals.id", ondelete="CASCADE"), index=True)
    file_id: Mapped[str] = mapped_column(String(256))
    kind: Mapped[str] = mapped_column(String(10))  # photo | video | document
