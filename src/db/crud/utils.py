import logging
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Concatenate, ParamSpec, TypeVar

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import async_session

logger = logging.getLogger('huitLogger')

P = ParamSpec("P")
T = TypeVar("T")

def err_handler(func: Callable[Concatenate[AsyncSession, P], Awaitable[T]]) -> Callable[P, Awaitable[tuple[T|None, bool]]]:
  """crud操作系の関数にエラーハンドリングを追加するデコレーターです

  Args:
    func (Callable[Concatenate[AsyncSession, P], Awaitable[T]]): crud操作関数

  Returns:
    Callable[P, Awaitable[tuple[T|None, bool]]]: _description_
  """
  @wraps(func)
  async def wrapper(*args: P.args, **kwargs: P.kwargs):
    async with async_session() as session:
      try:
        result = await func(session, *args, **kwargs)
        await session.commit()
        return result, False
      except SQLAlchemyError as e:
        await session.rollback()
        logger.exception(e)
        return None, True
  return wrapper
