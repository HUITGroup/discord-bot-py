""""CRUD操作部分"""

from datetime import date
from typing import Literal

import pandas as pd
from sqlalchemy import delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select

from db.database import async_session
from db.models import MemberRole, TimelineChannel, TimelineMessage, UserData


async def get_timeline_channel_id(guild_id: int):
  async with async_session() as session:
    result = await session.execute(
      select(TimelineChannel).where(TimelineChannel.guild_id == guild_id)
    )
    await session.commit()
    channel = result.scalar_one_or_none()
    return channel.timeline_id if channel else None


async def get_timeline_message_id(original_message_id: int):
  async with async_session() as session:
    result = await session.execute(
      select(TimelineMessage).where(
        TimelineMessage.original_message_id == original_message_id
      )
    )
    await session.commit()
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

async def get_member_role_id(guild_id: int):
  async with async_session() as session:
    result = await session.execute(
      select(MemberRole).where(MemberRole.guild_id == guild_id)
    )
    await session.commit()
    role = result.scalar_one_or_none()
    return role.member_role_id if role else None


async def register_message(timeline_message_id: int, original_message_id: int):
  async with async_session() as session:
    session.add(
      TimelineMessage(
        timeline_message_id=timeline_message_id,
        original_message_id=original_message_id,
      )
    )
    await session.commit()

async def get_user_by_username(user_name: str) -> UserData|None:
  async with async_session() as session:
    try:
      result = await session.get(UserData, user_name)
      await session.commit()
      return result
    except SQLAlchemyError as e:
      print(e)
      return None

async def get_users_by_deadline(deadline: date) -> list[UserData]:
  async with async_session() as session:
    try:
      result = await session.execute(
        select(UserData).where(UserData.deadline == deadline)
      )
      await session.commit()
      return list(result.scalars().all())
    except SQLAlchemyError as e:
      print(e)
      return []

async def get_all_users() -> list[UserData]:
  async with async_session() as session:
    try:
      result = await session.execute(select(UserData))
      await session.commit()
      return list(result.scalars().all())
    except SQLAlchemyError as e:
      print(e)
      return []

async def pre_register_user(username: str, nickname: str, grade: Literal['b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'm1', 'm2', 'd', 'other']):
  async with async_session() as session:
    try:
      user = await session.get(UserData, username)
      if user:
        user.grade = grade
      else:
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
      await session.rollback()
      print(e)
      return False

async def register_user(username: str, user_id: int, channel_id: int, deadline: date):
  async with async_session() as session:
    try:
      user = await session.get(UserData, username)
      print(user)
      if user:
        user.user_id = user_id
        user.channel_id = channel_id
        user.deadline = deadline
        await session.commit()
    except SQLAlchemyError as e:
      await session.rollback()
      print(e)


async def delete_user(user_id: int):
  async with async_session() as session:
    await session.execute(
      delete(UserData).where(UserData.user_id == user_id)
    )
    await session.commit()

async def csv_to_sql(df: pd.DataFrame):
  async with async_session() as session:
    objs = [UserData(**row) for row in df.to_dict(orient='records')]
    session.add_all(objs)
    await session.commit()
