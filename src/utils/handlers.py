from __future__ import annotations

import asyncio
import logging

import discord
from discord.ext import commands

from utils.constants import GUILD_ID, LEVELNAME_TO_COLOR, LOG_CHANNEL_ID

logger = logging.getLogger('textLogger')

class DiscordHandler(logging.Handler):
  """ログをDiscordのチャンネルに送信するハンドラー

  Args:
    logging (_type_): _description_
  """
  def __init__(self, bot: commands.Bot):
    super().__init__()
    self.bot = bot
    self.loop: asyncio.AbstractEventLoop|None = None

  def emit(self, record: logging.LogRecord):  # noqa: D102
    try:
      self.loop = asyncio.get_running_loop()
    except RuntimeError:
      logger.warning('Skipped: no running event loop')
      return

    if record.name.startswith('sqlalchemy.engine')\
    and (self.level == logging.INFO or self.level == logging.DEBUG):
      return

    message = self.format(record)
    if 'We are being rate limited.' in message:
      return
    coro = self.send_to_discord(message, record.levelname)
    asyncio.run_coroutine_threadsafe(coro, self.loop)

  async def send_to_discord(self, message: str, level: str):
    guild = self.bot.get_guild(GUILD_ID)
    if guild is None:
      logger.warning(
        'Skipped: either bot has no yet started or GUILD_ID is wrong'
      )
      return

    channel = guild.get_channel(LOG_CHANNEL_ID)
    assert isinstance(channel, discord.TextChannel)
    print(channel)
    if channel and message.strip():
      embed = discord.Embed(
        title=level,
        description=f"```\n{message[-1900:]}\n```",
        color=LEVELNAME_TO_COLOR[level],
      )
      await channel.send(embed=embed)
