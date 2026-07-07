import enum
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Enum, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class EventStatus(str, enum.Enum):
    pending = "pending"
    delivering = "delivering"
    delivered = "delivered"
    failed = "failed"


class Event(Base):
    __tablename__ = "events"
    __table_args__ = (
        UniqueConstraint("source", "external_id", name="uq_source_external_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    source: Mapped[str] = mapped_column(String(50))
    external_id: Mapped[str] = mapped_column(String(255))
    event_type: Mapped[str] = mapped_column(String(255))
    payload: Mapped[dict] = mapped_column(JSONB)

    status: Mapped[EventStatus] = mapped_column(
        Enum(EventStatus, name="event_status"), default=EventStatus.pending
    )
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    next_retry_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)