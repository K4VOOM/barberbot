from datetime import datetime, time, date

from sqlalchemy import (BigInteger, DateTime, Date, func, CheckConstraint, ForeignKey, Enum, MetaData,
                        UniqueConstraint, literal_column, text)
from sqlalchemy.dialects.postgresql import ExcludeConstraint
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention={
        "ix":"ix_%(column_0_label)s",
        "uq":"uq_%(table_name)s_%(column_0_N_name)s",
        "ck":"ck_%(table_name)s_%(constraint_name)s",
        "fk":"fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk":"pk_%(table_name)s"})

class User(Base):
    __tablename__ = "users"
    __table_args__ = (CheckConstraint("bonus_balance >= 0", name="bonus_non_negative"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    name: Mapped[str] = mapped_column()
    phone: Mapped[str] = mapped_column()
    language: Mapped[str] = mapped_column()
    referrer_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    bonus_balance: Mapped[int] = mapped_column(server_default="0")
    is_active: Mapped[bool] = mapped_column(default=True, server_default="true")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class Branch(Base):
    __tablename__ = "branches"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    address: Mapped[str] = mapped_column()
    work_hours_text: Mapped[str] = mapped_column()
    parking_text: Mapped[str | None] = mapped_column()
    google_url: Mapped[str | None] = mapped_column()
    apple_url: Mapped[str | None] = mapped_column()
    waze_url: Mapped[str | None] = mapped_column()
    photo_file_id: Mapped[str | None] = mapped_column()
    video_file_id: Mapped[str | None] = mapped_column()
    admin_tg_id: Mapped[int | None] = mapped_column(BigInteger)
    power_status: Mapped[str] = mapped_column(Enum(
        "power", "generator", "off",
        name="power_status_enum"),
        server_default="power"
    )
    power_note: Mapped[str | None] = mapped_column()
    power_updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    is_active: Mapped[bool] = mapped_column(default=True, server_default="true")

class Service(Base):
    __tablename__ = "services"
    __table_args__ = (
        CheckConstraint("price > 0", name="price_positive"),
        CheckConstraint("duration_min > 0", name="duration_positive")
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    category: Mapped[str] = mapped_column()
    name_uk: Mapped[str] = mapped_column()
    name_en: Mapped[str] = mapped_column()
    price: Mapped[int] = mapped_column()
    duration_min: Mapped[int] = mapped_column()
    is_active: Mapped[bool] = mapped_column(default=True, server_default="true")

class Master(Base):
    __tablename__ = "masters"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int | None] = mapped_column(BigInteger, unique=True)
    name: Mapped[str] = mapped_column()
    photo_file_id: Mapped[str | None] = mapped_column()
    specialization: Mapped[str] = mapped_column()
    rating: Mapped[float] = mapped_column(default=0, server_default="0")
    rating_count: Mapped[int] = mapped_column(default=0, server_default="0")
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"))
    is_active: Mapped[bool] = mapped_column(default=True, server_default="true")

class MasterService(Base):
    __tablename__ = "master_services"

    master_id: Mapped[int] = mapped_column(ForeignKey("masters.id", ondelete="CASCADE"), primary_key=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id", ondelete="CASCADE"), primary_key=True)

class Schedule(Base):
    __tablename__ = "schedules"
    __table_args__ = (
        CheckConstraint("weekday >= 0 AND weekday <= 6", name="weekday_range"),
        CheckConstraint("start_time < end_time", name="time_order"),
        CheckConstraint(
            "(break_start IS NULL AND break_end IS NULL) OR "
            "(break_start IS NOT NULL AND break_end IS NOT NULL AND "
            "break_start < break_end AND break_start >= start_time AND break_end <= end_time)",
            name="valid_break_times"
        ),
        UniqueConstraint("master_id", "weekday")
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    master_id: Mapped[int] = mapped_column(ForeignKey("masters.id", ondelete="CASCADE"))
    weekday: Mapped[int] = mapped_column()
    start_time: Mapped[time] = mapped_column()
    end_time: Mapped[time] = mapped_column()
    break_start: Mapped[time | None] = mapped_column()
    break_end: Mapped[time | None] = mapped_column()

class DayOff(Base):
    __tablename__ = "days_off"
    __table_args__ = (
        UniqueConstraint("master_id", "date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    master_id: Mapped[int] = mapped_column(ForeignKey("masters.id", ondelete="CASCADE"))
    date: Mapped[date] = mapped_column(Date)
    reason: Mapped[str | None] = mapped_column()

class Booking(Base):
    __tablename__ = "bookings"
    __table_args__ = (
        CheckConstraint("starts_at < ends_at", name="time_order"),
        CheckConstraint("price >= 0", name="price_non_negative"),
        CheckConstraint("discount >= 0 AND discount <= price", name="discount_valid"),
        CheckConstraint("bonus_used >= 0", name="bonus_used_non_negative"),
        CheckConstraint("bonus_used <= price - discount", name="bonus_used_valid"),
        ExcludeConstraint(
            ("master_id", "="),
            (func.tstzrange(literal_column("starts_at"), literal_column("ends_at")), "&&"),
            where=text("status IN ('new', 'confirmed', 'done')"),
            using="gist",
            name="no_overlap",
        )
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    master_id: Mapped[int] = mapped_column(ForeignKey("masters.id", ondelete="RESTRICT"))
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id", ondelete="RESTRICT"))
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id", ondelete="RESTRICT"))
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    price: Mapped[int] = mapped_column()
    discount: Mapped[int] = mapped_column(default=0, server_default="0")
    bonus_used: Mapped[int] = mapped_column(default=0, server_default="0")
    status: Mapped[str] = mapped_column(Enum("new", "confirmed", "done", "cancelled", "no_show", name="booking_status_enum"),server_default="new")
    is_hot: Mapped[bool] = mapped_column(default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    done_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    remind_24h_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    remind_2h_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    review_asked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    comeback_sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

class BonusTransaction(Base):
    __tablename__ = "bonus_transactions"
    __table_args__ = (
        CheckConstraint("amount != 0", name="amount_non_zero"),
        UniqueConstraint("booking_id", "reason"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    booking_id: Mapped[int | None] = mapped_column(ForeignKey("bookings.id", ondelete="RESTRICT"))
    amount: Mapped[int] = mapped_column()
    reason: Mapped[str] = mapped_column(Enum("cashback", "referral", "spend", "refund", "manual", name="bonus_transaction_reason_enum"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="rating_range"),
        UniqueConstraint("booking_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id", ondelete="CASCADE"))
    rating: Mapped[int] = mapped_column()
    comment: Mapped[str | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class Setting(Base):
    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(primary_key=True)
    value: Mapped[str] = mapped_column()