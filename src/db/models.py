"""モデル定義部分"""

from sqlalchemy import BigInteger, CheckConstraint, Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base


class TimelineChannel(Base):
  __tablename__ = "timeline_channel"
  guild_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
  timeline_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

class TimelineMessage(Base):
  __tablename__ = "timeline_message"
  timeline_message_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
  original_message_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

class MemberRole(Base):
  __tablename__ = "member_role_id"
  guild_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
  member_role_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
  year: Mapped[int] = mapped_column(Integer, nullable=False)

class UserData(Base):
  __tablename__ = "user_data"

  username: Mapped[str] = mapped_column(String(256), primary_key=True)
  user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
  nickname: Mapped[str] = mapped_column(String(256), nullable=False)
  grade: Mapped[str] = mapped_column(
    String(5),
    CheckConstraint(
      "grade IN ('b1', 'b2', 'b3', 'b4', 'b5', 'b6', "\
        "'m1', 'm2', 'd', 'other')",
      name="grade_check"
    ),
    nullable=False
  )
  channel_id: Mapped[int|None] = mapped_column(BigInteger)
  deadline: Mapped[Date|None] = mapped_column(Date)

class ArchiveCategory(Base):
  __tablename__ = "archive_channel"
  guild_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
  archive_category_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
  category_number: Mapped[int] = mapped_column(Integer, nullable=False)
