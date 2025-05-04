""""CRUD操作部分"""

from datetime import date
from typing import Literal

from sqlalchemy import delete, insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select

from src.db.database import async_session
from src.db.models import TimelineChannel, TimelineMessage, UserData


async def get_timeline_channel_id(guild_id: int):
  async with async_session() as session:
    result = await session.execute(
      select(TimelineChannel).where(TimelineChannel.guild_id == guild_id)
    )
    channel = result.scalar_one_or_none()
    return channel.timeline_id if channel else None


async def get_timeline_message_id(original_message_id: int):
  async with async_session() as session:
    result = await session.execute(
      select(TimelineMessage).where(
        TimelineMessage.original_message_id == original_message_id
      )
    )
    message = result.scalar_one_or_none()
    return message.timeline_message_id if message else None


async def del_timeline(original_message_id: int):
  async with async_session() as session:
    await session.execute(
      delete(TimelineMessage).where(
        TimelineMessage.original_message_id == original_message_id
      )
    )
    await session.commit()


async def register_timeline_channel(guild_id: int, channel_id: int):
  async with async_session() as session:
    existing = await session.get(TimelineChannel, guild_id)
    if existing:
      existing.timeline_id = channel_id
    else:
      session.add(TimelineChannel(guild_id=guild_id, timeline_id=channel_id))
    await session.commit()


async def register_message(timeline_message_id: int, original_message_id: int):
  async with async_session() as session:
    session.add(
      TimelineMessage(
        timeline_message_id=timeline_message_id,
        original_message_id=original_message_id,
      )
    )
    await session.commit()


async def get_users_by_deadline(deadline: date):
  async with async_session() as session:
    result = await session.execute(
      select(UserData.user_id).where(UserData.deadline == deadline)
    )
    return [r[0] for r in result.all()]

async def pre_register_user(username: str, nickname: str, grade: Literal['b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'm1', 'm2', 'd1', 'd2', 'd3', 'd', 'other']):
  async with async_session() as session:
    try:
      session.add(
        UserData(
          username=username,
          user_id=-1,
          nickname=nickname,
          grade=grade
        )
      )
      await session.commit()
      return True
    except SQLAlchemyError as e:
      session.rollback()
      print(e)
      return False

async def register_user(user_id: int, deadline: date):
  async with async_session() as session:
    exists = await session.get(UserData, user_id)
    if not exists:
      session.add(UserData(user_id=user_id, deadline=deadline))
      await session.commit()


async def delete_user(user_id: int):
  async with async_session() as session:
    await session.execute(
      delete(UserData).where(UserData.user_id == user_id)
    )
    await session.commit()
