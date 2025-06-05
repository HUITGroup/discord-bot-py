from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.crud.utils import err_handler
from src.db.models import MemberRole


@err_handler
async def update_member_role_id(
  session: AsyncSession,
  guild_id: int,
  member_role_id: int,
  year: int) -> None:
  """指定のmember roleのrole id、年度をサーバーと紐付けます

  Args:
    session (AsyncSession): _description_
    guild_id (int): サーバーのid
    member_role_id (int): member roleのrole id
    year (int): 年度
  """
  result = await session.get(MemberRole, guild_id)
  if result is None:
    session.add(MemberRole(guild_id=guild_id, member_role_id=member_role_id, year=year))
  else:
    result.member_role_id = member_role_id
    result.year = year

  await session.commit()

@err_handler
async def get_member_role_year(session: AsyncSession, guild_id: int) -> int|None:
  """現在紐付いているmember roleの年度を取得します

  Args:
    session (AsyncSession): _description_:
    guild_id (int): サーバーのid

  Returns:
    int|None: 現在紐付いているmember roleの年度。紐付いていない場合はNone
  """
  result = await session.get(MemberRole, guild_id)
  await session.commit()
  if result is None:
    return None
  else:
    return result.year

@err_handler
async def get_member_role_id(session: AsyncSession, guild_id: int) -> int|None:
  """現在紐付いているmember roleのrole idを取得します

  Args:
      session (AsyncSession): _description_
      guild_id (int): _description_

  Returns:
      _type_: _description_
  """
  result = await session.execute(
    select(MemberRole).where(MemberRole.guild_id == guild_id)
  )
  await session.commit()
  role = result.scalar_one_or_none()

  if role is None:
    return None
  else:
    return role.member_role_id
