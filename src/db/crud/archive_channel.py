from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.crud.utils import err_handler
from db.models import ArchiveCategory


@err_handler
async def get_latest_archive_category(
  session: AsyncSession,
  guild_id: int
) -> ArchiveCategory|None:
  subquery = (
    select(func.max(ArchiveCategory.category_number))
    .where(ArchiveCategory.guild_id == guild_id)
    .scalar_subquery()
  )

  stmt = (
    select(ArchiveCategory)
    .where(
      ArchiveCategory.guild_id == guild_id,
      ArchiveCategory.category_number == subquery
    )
  )

  res = await session.execute(stmt)
  return res.scalar_one_or_none()

@err_handler
async def create_archive_category(
  session: AsyncSession,
  guild_id: int,
  category_id: int,
  category_number: int,
) -> None:
  session.add(ArchiveCategory(
    guild_id=guild_id,
    archive_category_id=category_id,
    category_number=category_number,
  ))
  await session.commit()

@err_handler
async def get_archive_category_by_category_number(
  session: AsyncSession,
  guild_id: int,
  category_number: int,
) -> ArchiveCategory|None:
  result = await session.execute(
    select(ArchiveCategory).where(
      ArchiveCategory.guild_id == guild_id
      and ArchiveCategory.category_number == category_number
    )
  )

  return result.scalar_one_or_none()

@err_handler
async def sync_archive_category(
  session: AsyncSession,
  guild_id: int,
  category_id: int,
  category_number: int,
) -> None:
  result = await session.execute(
    select(ArchiveCategory).where(
      ArchiveCategory.guild_id == guild_id
      and ArchiveCategory.category_number == category_number
    )
  )
  category = result.scalar_one()

  category.guild_id = guild_id
  category.archive_category_id = category_id
  category.category_number = category_number
  await session.commit()
