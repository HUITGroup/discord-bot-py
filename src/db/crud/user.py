from datetime import date
from typing import Literal

import pandas as pd
from sqlalchemy import delete, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from db.crud.utils import err_handler
from db.models import UserData


@err_handler
async def reset_deadline(session: AsyncSession, username: str) -> None:
  """支払いチェックが済んだときなどに、その人の体験入部の期日を消去します

  Args:
    session (AsyncSession): _description_
    username (str): discordのusername
  """
  user = await session.get(UserData, username)
  if user:
    user.deadline = None
    await session.commit()
  else:
    raise NoResultFound(f'{username=}のユーザーが見つかりませんでした')


@err_handler
async def get_user_by_username(
  session: AsyncSession,
  username: str
) -> UserData|None:
  """discordのusernameから該当ユーザーを検索します

  Args:
    session (AsyncSession): _description_
    username (str): discordのusername

  Returns:
    UserData|None: 該当ユーザーのUserData。存在しない場合はNone
  """
  result = await session.get(UserData, username)
  # await session.commit()
  return result

@err_handler
async def get_user_by_nickname(
  session: AsyncSession,
  nickname: str
) -> UserData|None:
  """discordのニックネームから該当ユーザーを検索します

  Args:
    session (AsyncSession): _description_
    nickname (str): サーバーでのニックネーム

  Returns:
    UserData|None: 該当ユーザーのUserData。存在しない場合はNOne
  """
  result = await session.execute(
    select(UserData).where(UserData.nickname == nickname)
  )
  # await session.rollback()

  return result.scalar_one_or_none()

@err_handler
async def get_user_by_channel_id(
  session: AsyncSession,
  channel_id: int,
) -> UserData|None:
  """UserDataを紐づいているchannel idから検索します

  Args:
    session (AsyncSession): _description_
    channel_id (int): channel id

  Returns:
      UserData|None: _description_
  """
  result = await session.execute(
    select(UserData).where(UserData.channel_id == channel_id)
  )

  return result.scalar_one_or_none()

@err_handler
async def get_users_by_deadline(
  session: AsyncSession,
  deadline: date
) -> list[UserData]:
  """体験入部期間の期日がdeadlineと同じユーザーの一覧を取得します

  Args:
    session (AsyncSession): _description_
    deadline (date): 体験入部期間の期日

  Returns:
    list[UserData]: 該当ユーザーの一覧
  """
  result = await session.execute(
    select(UserData).where(UserData.deadline == deadline)
  )
  # await session.commit()
  return list(result.scalars().all())

@err_handler
async def get_all_users(session: AsyncSession) -> list[UserData]:
  """サーバーの全ユーザーを取得します

  Args:
    session (AsyncSession): _description_

  Returns:
    list[UserData]: ユーザー一覧
  """
  result = await session.execute(select(UserData))
  # await session.commit()
  return list(result.scalars().all())

@err_handler
async def update_username(
  session: AsyncSession,
  old_username: str,
  new_username: str
) -> None:
  """指定usernameのユーザーのusernameを更新します

  Args:
    session (AsyncSession): _description_
    old_username (str): _description_
    new_username (str): _description_

  Returns:
    _type_: _description_
  """
  result = await session.get(UserData, old_username)
  if result is None:
    raise NoResultFound(f'{old_username=}, {new_username=}のユーザーが見つかりませんでした')

  result.username = new_username
  await session.commit()

@err_handler
async def get_channel_id_by_user_id(
  session: AsyncSession,
  user_id: int
) -> int|None:
  """指定ユーザーに紐付いたtimesチャンネルのchannel idを取得します

  Args:
    session (AsyncSession): _description_
    user_id (int): discordのユーザーid

  Returns:
    int|None: ユーザーに紐付いたtimesチャンネルのchannel id。存在しない場合はNone
  """
  result = await session.execute(
    select(UserData).where(UserData.user_id == user_id)
  )
  # await session.commit()
  user = result.scalar_one_or_none()
  if user is None:
    return None
  else:
    return user.channel_id

@err_handler
async def pre_register_user(
  session: AsyncSession,
  username: str,
  nickname: str,
  grade: Literal['b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'm1', 'm2', 'd', 'other']
) -> None:
  """ユーザーの事前登録を行います。discordのusername、サーバーでのニックネーム、学年を登録します。すでに存在するユーザーの場合はニックネームと学年を更新します

  Args:
    session (AsyncSession): _description_
    username (str): discordのusername
    nickname (str): サーバーでのニックネーム
    grade (Literal[&#39;b1&#39;, &#39;b2&#39;, &#39;b3&#39;, &#39;b4&#39;, &#39;b5&#39;, &#39;b6&#39;, &#39;m1&#39;, &#39;m2&#39;, &#39;d&#39;, &#39;other&#39;]): 学年
  """
  user = await session.get(UserData, username)
  if user:
    user.grade = grade
    user.nickname = nickname
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

@err_handler
async def register_user(
  session: AsyncSession,
  username: str,
  user_id: int,
  channel_id: int,
  deadline: date
) -> None:
  """ユーザーの本登録を行います。ユーザーのuser id、timesのchannel id、体験入部期間の期日を登録します。

  Args:
    session (AsyncSession): _description_
    username (str): discordのusername
    user_id (int): discordのuser id
    channel_id (int): timesのchannel id
    deadline (date): 体験入部期間の期日
  """
  user = await session.get(UserData, username)
  if user:
    user.user_id = user_id
    user.channel_id = channel_id
    user.deadline = deadline
    await session.commit()

@err_handler
async def delete_user(session: AsyncSession, user_id: int):
  """ユーザーのレコードを削除します

  Args:
    session (AsyncSession): _description_
    user_id (int): discordのuser id
  """
  await session.execute(
    delete(UserData).where(UserData.user_id == user_id)
  )
  await session.commit()

@err_handler
async def csv_to_sql(session: AsyncSession, df: pd.DataFrame):
  objs = [UserData(**row) for row in df.to_dict(orient='records')]
  session.add_all(objs)
  await session.commit()

@err_handler
async def csv_to_sql_each_row(session: AsyncSession, df: pd.DataFrame):
  for row in df.to_dict(orient='records'):
    result = await session.get(UserData, row['username'])
    if result is None:
      session.add(UserData(**row))

  await session.commit()
