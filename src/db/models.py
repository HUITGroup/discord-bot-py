"""モデル定義部分"""

from sqlalchemy import BigInteger, CheckConstraint, Column, Date, String

from src.db.database import Base


class TimelineChannel(Base):
  __tablename__ = "timeline_channel"
  guild_id = Column(BigInteger, primary_key=True)
  timeline_id = Column(BigInteger, nullable=False)

class TimelineMessage(Base):
  __tablename__ = "timeline_message"
  timeline_message_id = Column(BigInteger, primary_key=True)
  original_message_id = Column(BigInteger, nullable=False)

class UserData(Base):
  __tablename__ = "user_data"
  username = Column(String, primary_key=True)
  user_id = Column(BigInteger, nullable=False)
  nickname = Column(String, nullable=False)
  grade = Column(
    String,
    CheckConstraint(
      "grade IN ('b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'm1', 'm2', 'd1', 'd2', 'd3', 'd', 'other')",
      name="grade_check"
    ),
    nullable=False
  )
  deadline = Column(Date)
