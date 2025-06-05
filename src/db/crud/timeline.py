from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.crud.utils import err_handler
from db.models import TimelineChannel, TimelineMessage


@err_handler
async def get_timeline_channel_id(session: AsyncSession, guild_id: int) -> int|None:
  """指定のguild_idに紐付いたtimelineチャンネルのchannel idを取得します

  Args:
    session (AsyncSession): _description_
    guild_id (int): discordサーバーのサーバーid

  Returns:
    int|None: timelineチャンネルのchannel id。登録されていない場合はNone
  """
  result = await session.get(TimelineChannel, guild_id)
  await session.commit()

  if result is None:
    return None
  else:
    return result.timeline_id

@err_handler
async def get_timeline_message_id(
  session: AsyncSession,
  original_message_id: int
) -> int|None:
  """指定のmessage idに紐付いたtimelineのメッセージのmessage idを返します

  Args:
    session (AsyncSession): _description_
    original_message_id (int): 元のメッセージのmessage id

  Returns:
    int|None: timelineのメッセージのmessage id。存在しない場合はNone
  """
  result = await session.execute(
    select(TimelineMessage).where(
      TimelineMessage.original_message_id == original_message_id
    )
  )
  await session.commit()
  message = result.scalar_one_or_none()

  if message is None:
    return None
  else:
    return message.timeline_message_id

@err_handler
async def register_message(
  session: AsyncSession,
  timeline_message_id: int,
  original_message_id: int
) -> None:
  """元のメッセージと対応するtimelineメッセージのmessage idのペアを登録します

  Args:
    session (AsyncSession): _description_
    timeline_message_id (int): 対応するtimelineメッセージのmessage id
    original_message_id (int): 元のメッセージのmessage id
  """
  session.add(
    TimelineMessage(
      timeline_message_id=timeline_message_id,
      original_message_id=original_message_id,
    )
  )
  await session.commit()

@err_handler
async def delete_timeline(session: AsyncSession, original_message_id: int) -> None:
  """メッセージに対応するレコードを削除します

  Args:
    session (AsyncSession): _description_
    original_message_id (int): 元のメッセージのmessage id
  """
  await session.execute(
    delete(TimelineMessage).where(
      TimelineMessage.original_message_id == original_message_id
    )
  )
  await session.commit()

@err_handler
async def register_timeline_channel(
  session: AsyncSession,
  guild_id: int,
  channel_id: int
) -> None:
  """指定したguild id、channel idのペアを登録します。guild idが存在する場合はchannel idが上書きされます

  Args:
    session (AsyncSession): _description_
    guild_id (int): サーバーのid
    channel_id (int): timelineチャンネルのchannel id
  """  # noqa: E501
  existing = await session.get(TimelineChannel, guild_id)
  if existing:
    existing.timeline_id = channel_id
  else:
    session.add(TimelineChannel(guild_id=guild_id, timeline_id=channel_id))
  await session.commit()
